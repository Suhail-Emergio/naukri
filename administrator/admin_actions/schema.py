from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import timedelta
from jobs.job_actions.schema import ApplyCandidatesData

class PlanCreation(Schema):
    title: str
    description: Dict[str, str]
    posts: int
    duration: timedelta
    audience: str
    resdex: bool = False
    rate: int
    feature: bool = False

PlanData = create_schema(Plans)

class BannerCreation(Schema):
    image: str

BannerData = create_schema(Banner)

class ApplicationStats(Schema):
    applications: List[ApplyCandidatesData]
    views: int
    candidates: int
    shortlisted: int
    rejected: int