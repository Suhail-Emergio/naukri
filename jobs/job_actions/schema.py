from ninja import Schema, FilterSchema, Field
from typing import *
from ninja.orm import create_schema
from .models import *
from jobs.jobposts.schema import JobCompanyData
from datetime import datetime

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
    job: JobCompanyData
    custom_qns: Optional[List[str]]
    status: str
    viewed: bool
    created_on: datetime