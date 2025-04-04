from ninja import Schema, FilterSchema, Field
from typing import *
from ninja.orm import create_schema
from .models import *
from jobs.jobposts.schema import JobCompanyData, JobData
from datetime import datetime
from recruiter.recruiter_actions.schema import SeekerData
from recruiter.company.schema import CompanyData

# Job Post to save Schema
class SavedJobsCreation(Schema):
    job_id : int

class SavedJobsData(Schema):
    job: JobCompanyData
    created_on: datetime

# Job Post to apply Schema
class ApplyJobsCreation(Schema):
    """
    ApplyJobsCreation schema for job application creation.

    Attributes:
        job_id (int): The unique identifier for the job.
        custom_qns (Optional[List[str]]): A list of custom questions for the job application. Defaults to None.
    """
    job_id : int
    custom_qns : Optional[List[str]] = None

class ApplyJobsData(Schema):
    id: int
    job: JobCompanyData
    custom_qns: Optional[Union[List[str], Dict[str, Any]]]
    status: str
    viewed: bool
    created_on: datetime

class ApplyCandidatesData(Schema):
    id: int
    job: JobData
    company: CompanyData
    applied_jobs: List[JobData]
    candidate: SeekerData
    custom_qns: Optional[Union[List[str], Dict[str, Any]]]
    matching_skills : Optional[List[str]]
    status: str
    viewed: bool
    created_on: datetime
    phone: str | None = None