import httpx
from services.rest_core import RestCore

from models.models import Event
from services.token_service import TokenService


class EventService(RestCore):
    _BASE_URL = "http://localhost:8000"
    _instance = None
    _token_service = None

    def __init__(self, BASE_URL: str = _BASE_URL):
        super().__init__(BASE_URL)

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = EventService()
            cls._token_service = await TokenService.get_instance()
        return cls._instance

    async def check_health(self):
        response = await self.get("/health")
        return response.status_code == 200

    async def get_task_status(self, task_id: str, user, password):
        response = await self.get(
            f"/status/{task_id}",
            headers={"Authorization": f"Bearer {await self._token(user, password)}"},
        )
        return response.json()

    async def create_event(self, body, user, password):
        response = await self.post(
            "/event",
            data=body,
            headers={"Authorization": f"Bearer {await self._token(user, password)}"},
        )
        if response.status_code != httpx.codes.ACCEPTED:
            raise Exception(f"Failed to create event {response.json()}")
        return Event(
            task_id=response.json()["task_id"],
            data=body.get('data')
        )

    async def _token(self, user, password):
        response = await self._token_service.get_current_token(user, password)
        return response
