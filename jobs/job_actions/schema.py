from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

# Job Post to save Schema
class SavedJobsCreation(Schema):
    job_id : int

SavedJobsData = create_schema(SaveJobs)

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

ApplyJobsData = create_schema(ApplyJobs)

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