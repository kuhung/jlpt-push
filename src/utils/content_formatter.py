from typing import Dict, List, Tuple
import random

class ContentFormatter:
    @staticmethod
    def format_grammar(grammar: Dict) -> str:
        """
        格式化单条语法内容为推送文本
        :param grammar: 语法点字典
        :return: 格式化后的字符串
        """
        # TODO: 实现格式化逻辑
        return ""

    @staticmethod
    def format_examples(examples: List[Dict]) -> str:
        """
        格式化例句列表
        :param examples: 例句列表
        :return: 格式化后的字符串
        """
        # TODO: 实现格式化逻辑
        return ""

    @staticmethod
    def format_for_push(grammar_item: Dict, config: Dict) -> Tuple[str, str, str]:
        """
        根据配置模板格式化单条语法内容为推送格式。
        
        :param grammar_item: 单条语法点字典
        :param config: 应用配置字典
        :return: (推送标题, 推送正文, 推送URL)
        """
        push_config = config.get('push', {})
        title_template = push_config.get('format', {}).get('title_template', "{title}")
        body_template = push_config.get('format', {}).get('body_template', "{usage}\n{meaning}\n{example}")

        # 准备模板替换所需的数据
        # 随机选择一个例句
        example_jp = ""
        if grammar_item.get("examples"):
            example = random.choice(grammar_item["examples"])
            example_jp = example.get("jp", "")

        format_data = {
            "title": grammar_item.get("title", ""),
            "pattern": grammar_item.get("pattern", ""),
            "usage": grammar_item.get("usage", ""),
            "meaning": grammar_item.get("meaning", ""),
            "level": grammar_item.get("level", ""),
            "notes": grammar_item.get("notes", ""),
            "example": example_jp,
        }
        
        # 渲染模板
        title = title_template.format(**format_data)
        body = body_template.format(**format_data)
        
        # 准备 URL
        url = grammar_item.get("source_url", "")

        return title, body, url 