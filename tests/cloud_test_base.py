import random

from models.models import Event
from services.event_service import EventService
import asyncio
import time
import traceback

class TestBase:

    _event_svc = None

    async def run_e2e_workflow(self, user, password):

        # Initalize start_time and event object for each event
        start_time = time.time()
        event = Event(task_id="N/A", data={}, status="pending")

        try:
            # Init Event Service
            self._event_svc = await self._get_event_service()

            test_data = await self._get_random_test_data()
            
            # workflows
            event = await self._event_svc.create_event(test_data, user, password)
            await self.poll_status(event, user, password)
    
            return {
                "task_id": event.task_id,
                "status": "PASSED",
                "time_taken": f"{time.time() - start_time:.2f}s"
            }
        except Exception as e:
            return {
                "task_id": event.task_id or "N/A",
                "status": "FAILED",
                "time_taken": f"{time.time() - start_time:.2f}s",
                "reason": str(e)
            }

    async def poll_status(self, event: Event, user, password):
        delay = 25 # Slightly more than the least processing time
        max_total_time = 190 # Slight more than the maximum processing time
        
        start_time = time.time()

        while time.time() - start_time < max_total_time:
            await asyncio.sleep(delay)

            # Check if we would exceed total time limit
            if time.time() - start_time >= max_total_time:
                break

            status = await self._event_svc.get_task_status(event.task_id, user, password)

            if status.get("data") != event.data:
                raise Exception(f"Data mismatch between request {event.data} and response {status.get('data')}")

            delay = min(delay * 1.5, 60)  # Cap individual delay at 60s

            if status.get("status") == "settled":
                event.status = "settled"
                return
            elif status.get("status") == "pending":
                print(f"Task {event.task_id} is still pending. Retrying after {delay}s")

        raise Exception(f"Polling timeout after {max_total_time}s - event still pending")

    async def _get_event_service(self):
        if self._event_svc is None:
            self._event_svc = await EventService.get_instance()
        return self._event_svc

    async def _get_random_test_data(self):
        mock_test_data = [
            {"data": {"user_id": "123", "action": "unlocked secret level"}},
            {"data": {"user_id": "123", "action": "discovered hidden feature"}},
            {"data": {"user_id": "123", "action": "earned achievement badge"}},
            {"data": {"user_id": "123", "action": "joined beta program"}},
            {"data": {"user_id": "123", "action": "shared on social media"}},
            {"data": {"user_id": "123", "action": "redeemed promo code"}},
            {"data": {"user_id": "123", "action": "completed tutorial"}},
            {"data": {"user_id": "123", "action": "customized avatar"}},
            {"data": {"user_id": "123", "action": "created playlist"}},
            {"data": {"user_id": "123", "action": "invited a friend"}},
        ]
        return random.choices(mock_test_data)[0]
