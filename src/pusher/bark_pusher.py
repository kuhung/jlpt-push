import aiohttp
import logging
import asyncio
from typing import Dict
from urllib.parse import quote

class BarkPusher:
    def __init__(self, config: Dict):
        bark_config = config.get('bark', {})
        self.api_key = bark_config.get('key', '')
        if not self.api_key or self.api_key == 'YOUR_BARK_KEY':
            raise ValueError("Bark API key 未在配置文件中设置。")
        self.base_url = bark_config.get('url', 'https://api.day.app')
        self.logger = logging.getLogger(__name__)
        self.max_retries = bark_config.get('max_retries', 3)
        self.base_delay = bark_config.get('base_delay', 1)

    async def push(self, title: str, body: str, url: str = "") -> bool:
        """
        推送内容到Bark。

        :param title: 推送标题
        :param body: 推送正文
        :param url: 点击推送后跳转的URL
        :return: 推送是否成功
        """
        if not title:
            self.logger.warning("推送标题为空，取消推送。")
            return False

        # URL编码
        title_encoded = quote(title)
        body_encoded = quote(body)
        
        # 构建请求URL
        push_url = f"{self.base_url}/{self.api_key}/{title_encoded}/{body_encoded}"
        
        params = {}
        if url:
            params['url'] = url
            
        for attempt in range(self.max_retries):
            self.logger.info(f"正在推送到 Bark (尝试 {attempt + 1}/{self.max_retries}): {title}")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(push_url, params=params) as response:
                        if response.status == 200:
                            self.logger.info(f"推送成功: {title}")
                            return True
                        else:
                            response_text = await response.text()
                            self.logger.error(f"推送失败，状态码: {response.status}, 响应: {response_text}")
            except aiohttp.ClientError as e:
                self.logger.error(f"推送请求出错 (尝试 {attempt + 1}/{self.max_retries}): {e}")
            
            if attempt < self.max_retries - 1:
                delay = self.base_delay * (2 ** attempt)
                self.logger.info(f"等待 {delay} 秒后重试...")
                await asyncio.sleep(delay)
        
        self.logger.error(f"达到最大重试次数，推送最终失败: {title} (推送URL: {push_url})")
        return False 