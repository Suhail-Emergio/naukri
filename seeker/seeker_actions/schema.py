from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import date
from jobs.jobposts.schema import JobData

# Personal Schema
class JobInvitations(Schema):
    job: JobData
    read: bool
    created_on: str