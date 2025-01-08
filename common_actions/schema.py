from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from administrator.admin_actions.schema import PlanData
from datetime import datetime

class SuggestionCreation(Schema):
    suggestions: str

class SubscriptionCreation(Schema):
    plan_id: int
    transaction_id: str

class SubscriptionData(Schema):
    id: int
    plan_id: PlanData
    remaining_posts: int
    transaction_id: str
    subscribed_on: datetime