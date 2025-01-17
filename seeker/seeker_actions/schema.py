from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import date, datetime
from jobs.jobposts.schema import JobData
from recruiter.company.models import CompanyDetails

class JobInvitations(Schema):
    job: JobData
    read: bool
    interested: bool
    created_on: datetime

class BlockedComp(Schema):
    company: CompanyDetails
    blocked_on: datetime