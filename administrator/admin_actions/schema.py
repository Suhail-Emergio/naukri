from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import timedelta

class PlanCreation(Schema):
    title: str
    description: Dict[str, str]
    posts: int
    duration: timedelta
    audience: str
    rate: int
    feature: bool = False

PlanData = create_schema(Plans)

class BannerCreation(Schema):
    image: str

BannerData = create_schema(Banner)