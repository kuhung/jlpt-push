import aiohttp
import logging
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
            
        self.logger.info(f"正在推送到 Bark: {title}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(push_url, params=params) as response:
                    if response.status == 200:
                        self.logger.info(f"推送成功: {title}")
                        return True
                    else:
                        response_text = await response.text()
                        self.logger.error(f"推送失败，状态码: {response.status}, 响应: {response_text}")
                        return False
        except aiohttp.ClientError as e:
            self.logger.error(f"推送请求出错: {e}")
            return False 