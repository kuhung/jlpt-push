import json
import logging
import os
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class GrammarConverter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 定义section标记
        self.sections = {
            "meaning": "[意味]",
            "usage": "[接続]",
            "level": "[JLPT レベル]",
            "notes": "[備考]",
            "examples": "例文"
        }

    def convert(self, raw_data: List) -> Dict:
        """
        将原始 term_bank_6.json 数据转换为结构化的语法点数据。
        :param raw_data: 原始数据列表
        :return: 结构化后的字典
        """
        grammar_list = []
        for idx, item in enumerate(raw_data):
            try:
                # 基础信息提取
                grammar_item = {
                    "id": f"gram_{idx+1:03d}",
                    "title": item[0].strip(),
                    "reading": item[1].strip(),
                    "pattern": item[2].strip().replace("・", ""),
                    "type": item[3].strip(),
                    "source_name": item[7].strip() if len(item) > 7 else "",
                    "tags": []
                }

                # 解析内容块
                content_block = item[5][0]["content"] if item[5] and isinstance(item[5][0], dict) else []
                text_content, source_url = self._extract_content_and_url(content_block)
                
                # 清理文本内容
                text_content = self._clean_text(text_content)
                
                # 解析各个部分
                sections = self._parse_sections(text_content)
                grammar_item.update(sections)
                
                # 提取例句
                grammar_item["examples"] = self.extract_examples(text_content)
                
                # 添加来源URL
                grammar_item["source_url"] = source_url

                grammar_list.append(grammar_item)
                self.logger.info(f"成功解析第 {idx+1} 条语法数据：{grammar_item['title']}")
                
            except Exception as e:
                self.logger.error(f"解析第 {idx+1} 条数据出错: {str(e)}")
                # 保存部分解析结果
                if 'grammar_item' in locals():
                    grammar_item["parse_error"] = str(e)
                    grammar_list.append(grammar_item)

        return {
            "version": "1.0",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(grammar_list),
            "grammar": grammar_list
        }

    def _extract_content_and_url(self, content_block: List) -> Tuple[str, str]:
        """提取内容文本和URL"""
        text_content = ""
        source_url = ""
        for item in content_block:
            if isinstance(item, str):
                text_content += item
            elif isinstance(item, dict) and item.get("tag") == "a":
                source_url = item.get("href", "")
        return text_content, source_url

    def _clean_text(self, text: str) -> str:
        """清理文本内容"""
        # 移除广告代码
        text = re.sub(r'\(adsbygoogle.*?\);', '', text)
        # 移除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    def _parse_sections(self, text: str) -> Dict:
        """解析文本中的各个部分"""
        result = {}
        
        # 提取意义
        meaning = self._extract_between(text, self.sections["meaning"], self.sections["usage"])
        result["meaning"] = self._clean_section(meaning)
        
        # 提取用法
        usage = self._extract_between(text, self.sections["usage"], self.sections["level"])
        result["usage"] = self._clean_section(usage)
        
        # 提取JLPT等级
        level = self._extract_between(text, self.sections["level"], self.sections["notes"])
        if not level:  # 如果没有备考部分，尝试到例文
            level = self._extract_between(text, self.sections["level"], self.sections["examples"])
        result["level"] = self._clean_section(level)
        
        # 提取备注
        notes = self._extract_between(text, self.sections["notes"], self.sections["examples"])
        result["notes"] = self._clean_section(notes)
        
        return result

    def _clean_section(self, text: str) -> str:
        """清理段落内容"""
        if not text:
            return ""
        # 移除空行
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        # 移除项目符号
        lines = [line[1:].strip() if line.startswith('・') else line for line in lines]
        return '\n'.join(lines)

    def extract_examples(self, content: str) -> List[Dict]:
        """
        从内容中提取例句。
        :param content: 包含例句的字符串
        :return: 例句列表
        """
        examples = []
        if self.sections["examples"] not in content:
            return examples

        # 获取例文部分
        example_text = content.split(self.sections["examples"], 1)[1]
        # 分割成行
        lines = [line.strip() for line in example_text.split('\n') if line.strip()]
        
        current_jp = None
        for line in lines:
            # 跳过标题行和分隔符
            if line.startswith('【') or line.startswith('[') or '(adsbygoogle' in line:
                continue
                
            # 处理项目符号
            if line.startswith('・'):
                line = line[1:].strip()
                
            # 如果是空行，跳过
            if not line:
                continue
                
            # 检查是否包含日语字符
            has_jp = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', line))
            
            if has_jp:
                # 如果之前有未配对的日语句子，保存它
                if current_jp:
                    examples.append({"jp": current_jp, "en": ""})
                current_jp = line
            elif current_jp:
                # 英文翻译
                examples.append({"jp": current_jp, "en": line})
                current_jp = None
            
        # 处理最后一个未配对的日语句子
        if current_jp:
            examples.append({"jp": current_jp, "en": ""})
            
        return examples

    def _extract_between(self, text: str, start: str, end: str) -> str:
        """提取两个标记之间的内容"""
        if start not in text:
            return ""
        parts = text.split(start, 1)
        if len(parts) < 2:
            return ""
        text = parts[1]
        if end in text:
            text = text.split(end, 1)[0]
        return text.strip()

def main():
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        converter = GrammarConverter()
        raw_path = os.path.join(os.path.dirname(__file__), '../../data/raw/term_bank_3.json')
        out_path = os.path.join(os.path.dirname(__file__), '../../data/processed/grammar_bank.json')
        
        # 检查输入文件
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"找不到输入文件：{raw_path}")
            
        # 读取原始数据
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        if not raw_data:
            raise ValueError("输入文件为空")
            
        # 转换数据
        result = converter.convert(raw_data)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        # 写入结果
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        print(f"转换完成！共处理 {len(raw_data)} 条数据")
        print(f"输出文件：{out_path}")
        
    except Exception as e:
        logging.error(f"转换过程出错：{str(e)}")
        raise

if __name__ == '__main__':
    main() 