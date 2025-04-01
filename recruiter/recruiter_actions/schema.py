from ninja import Schema
from typing import *
from ninja.orm import create_schema
from seeker.details.schema import *
from .models import *
from datetime import datetime
from jobs.jobposts.schema import JobData

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
    employment: Optional[List[EmploymentData]] = None
    qualification: Optional[List[QualificationData]] = None

class InviteCandidateSchema(Schema):
    candidate_id: int
    job_id: int

class JobInvites(Schema):
    id: int
    candidate: SeekerData
    job: JobData
    read: bool
    created_on: str
    status: str

EmailTemplates = create_schema(EmailTemplate)

class TemplateCreation(Schema):
    name: str
    subject : str
    body : str
    job_id : int

class ScheduledInterviews(Schema):
    id: int
    candidate: SeekerData
    job: JobData
    interview_round: Optional[str] = None
    schedule: datetime
    created_on: str

class InterviewScheduleSchema(Schema):
    candidate_id: int
    job_id: int
    schedule: datetime

class ResumeDownloadSchema(Schema):
    candidate: PersonalSchema
    job: JobData

class UpdateApplicationStatus(Schema):
    status : str

class UpdateInterviewRound(Schema):
    interview_round : str
    interview_status : str
    schedule : datetime

class ViewedCandidateSchema(Schema):
    id: int
    candidate: SeekerData
    viewed_on: str

class SavedCandidateSchema(Schema):
    id: int
    candidate: SeekerData
    created_on: str