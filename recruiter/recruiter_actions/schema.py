from ninja import Schema
from typing import *
from ninja.orm import create_schema
from seeker.details.schema import *
from .models import *
from datetime import datetime

class SearchCriteria(Schema):
    keywords: Optional[List[str]] = None
    experience_year: Optional[int] = None
    experience_month: Optional[int] = None
    current_loc: Optional[str] = None
    nationality: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    gender: Optional[str] = None
    additional: Optional[str] = None

class SeekerData(Schema):
    personal : PersonalSchema
    # employment: List[Optional[EmploymentData]] = None
    employment: Optional[List[EmploymentData]] = None
    qualification: Optional[List[QualificationData]] = None
    # qualification: List[Optional[QualificationData]] = None

class InviteCandidateSchema(Schema):
    candidate_id: int
    job_id: int

class JobInvites(Schema):
    candidate: SeekerData
    job: JobData
    read: bool

EmailTemplates = create_schema(EmailTemplate)

class TemplateCreation(Schema):
    name: str
    subject : str
    body : str
    job_id : int

class ScheduledInterviews(Schema):
    candidate: SeekerData
    schedule: datetime
    created_on: datetime

class InterviewScheduleSchema(Schema):
    candidate_id: int
    job_id: int
    schedule: datetime