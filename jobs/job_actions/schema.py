from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from jobs.jobposts.schema import JobCompanyData
from datetime import datetime

# Job Post to save Schema
class SavedJobsCreation(Schema):
    job_id : int

class SavedJobsData(Schema):
    job: List[JobCompanyData]
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
    job: List[JobCompanyData]
    custom_qns: Optional[List[str]]
    status: str
    viewed: str
    created_on: datetime

class FilterQuery(Schema):
    specialization: str = None
    query: str = None
    filter: bool = False
    job_category: str = None
    job_type: str = None
    city: str = None
    salary_min: int = None
    salary_max: int = None
    experience_min : int = None
    experience_max : int = None
    freshness: int = None