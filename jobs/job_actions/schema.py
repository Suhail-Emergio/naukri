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
    job_id : int

ApplyJobsData = create_schema(ApplyJobs)