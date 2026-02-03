import httpx
from src.config import API_BASE_URL, CAFE_API_KEY
from src.utils.http_client import HttpClient
from src.utils.logger import logger

class BackendService:
    @staticmethod
    async def get_registration(audit_code: str):
        headers = {}
        if CAFE_API_KEY:
            headers["Cafe-API-Key"] = CAFE_API_KEY
            
        client = await HttpClient.get_client()
        try:
            response = await client.get(
                f"{API_BASE_URL}/registrations/{audit_code}", 
                headers=headers
            )
            return response
        except httpx.RequestError as e:
            logger.error(f"Backend request error: {e}", exc_info=True)
            raise
