import asyncio
import json
import logging
import os
import random
import yaml
from typing import Dict, Any

from src.pusher.bark_pusher import BarkPusher
from src.utils.content_formatter import ContentFormatter

# 全局路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'config.yaml')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'grammar_bank.json')
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'push.log')

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"配置文件未找到: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def setup_logging(config: Dict[str, Any]):
    """设置日志"""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO').upper(), logging.INFO)
    
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def load_grammar_data() -> Dict[str, Any]:
    """加载处理后的语法数据"""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"语法数据文件未找到: {DATA_PATH}。请先运行转换脚本。")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

async def main():
    """主执行函数"""
    try:
        # 1. 加载配置和设置日志
        config = load_config()
        setup_logging(config)
        logger = logging.getLogger(__name__)

        # 2. 加载语法数据
        logger.info("正在加载语法数据...")
        grammar_data = load_grammar_data()
        grammar_list = grammar_data.get('grammar', [])
        if not grammar_list:
            logger.warning("语法数据为空，无法推送。")
            return

        # 3. 随机选择一条语法
        selected_grammar = random.choice(grammar_list)
        logger.info(f"已选择语法点: {selected_grammar['title']}")

        # 4. 格式化内容
        title, body, url = ContentFormatter.format_for_push(selected_grammar, config)

        # 5. 执行推送
        pusher = BarkPusher(config)
        success = await pusher.push(title, body, url)

        if success:
            logger.info("推送任务成功完成。")
        else:
            logger.error("推送任务失败。")

    except FileNotFoundError as e:
        logging.error(f"文件错误: {e}")
    except ValueError as e:
        logging.error(f"配置错误: {e}")
    except Exception as e:
        logging.error(f"发生未知错误: {e}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(main()) 