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

    @staticmethod
    async def upload_logs(logs: list):
        if not logs:
            return
            
        headers = {}
        if CAFE_API_KEY:
            headers["Cafe-API-Key"] = CAFE_API_KEY
            
        client = await HttpClient.get_client()
        try:
            response = await client.post(
                f"{API_BASE_URL}/logs", 
                json=logs,
                headers=headers
            )
            if response.status_code != 200:
                logger.error(f"Failed to upload logs. Status: {response.status_code}, Response: {response.text}")
            return response
        except httpx.RequestError as e:
            logger.error(f"Backend request error during log upload: {e}", exc_info=True)
            # We don't want to raise here to avoid crashing the background task, 
            # but we might want to keep the logs for next time.
            # However, for simplicity now, we just log it.
            raise
