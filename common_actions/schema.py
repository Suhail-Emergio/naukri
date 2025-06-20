from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from administrator.admin_actions.schema import PlanData
from datetime import datetime

class SuggestionCreation(Schema):
    suggestion: str

class SubscriptionCreation(Schema):
    plan_id: int
    transaction_id: str

class SubscriptionData(Schema):
    id: int
    plan: PlanData
    remaining_posts: int
    transaction_id: str
    subscribed_on: datetime

class subscriptionstatus(Schema):
    message: str
    resdex: bool

class NotificationCreation(Schema):
    user_id: Optional[List[int]] = None
    audience: str | None = None
    title: str
    description: str
    url: Optional[str]

class NotificationSchema(Schema):
    title: str
    description: str
    image: Optional[str]
    url: Optional[str]
    created_on: datetime

class NotificationData(Schema):
    id: int
    noti: NotificationSchema
    read: bool