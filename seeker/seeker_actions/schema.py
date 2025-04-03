from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import date, datetime
from jobs.jobposts.schema import JobData, JobCompanyData
from recruiter.company.schema import CompanyData

class JobInvitations(Schema):
    id: int
    job: JobCompanyData
    read: bool
    status: str
    created_on: datetime

class BlockedComp(Schema):
    company: CompanyData
    blocked_on: datetime

class StatusUpdate(Schema):
    status: str