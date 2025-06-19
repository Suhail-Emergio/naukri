from pydantic import BaseModel
from typing import Dict, Optional

class NotificationCount(BaseModel):
    notification_count: int
    invitation_count: int

class WSMessage(BaseModel):
    type: str
    data: Dict