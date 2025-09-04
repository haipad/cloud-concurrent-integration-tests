from typing import Dict, Literal
from pydantic import BaseModel


class Token(BaseModel):
    """Model representing token and its properties"""

    access_token: str
    expiry_sec: int
    creation_ts: float | None


class EventRequest(BaseModel):
    data: Dict[str, str]


class Event(BaseModel):
    """Model representing a event and its properties"""

    task_id: str
    data: Dict[str, str]
    status: Literal["pending", "settled"] | None = "pending"
