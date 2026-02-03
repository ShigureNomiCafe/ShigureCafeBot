import httpx
from src.config import PROXY_URL
from src.utils.logger import logger

class HttpClient:
    _client: httpx.AsyncClient = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            # Backend requests usually don't need a proxy. 
            # Telegram API proxy is handled separately in main.py.
            cls._client = httpx.AsyncClient(timeout=15.0)
        return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info("HTTP client closed.")
