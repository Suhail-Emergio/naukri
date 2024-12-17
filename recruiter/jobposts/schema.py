from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

# Job Post Schema
class JobCreation(Schema):
    user : int
    title : str
    description : str
    type : str
    country : str
    vacancy : int
    industry : str
    functional_area : str
    gender : Optional[str] = None
    nationality : Optional[str] = None
    experience_min : Optional[int] = None
    experience_max : Optional[int] = None
    candidate_location : Optional[str] = None
    education : Optional[str] = None
    salary_min : Optional[int] = None
    salary_max : Optional[int] = None

JobData = create_schema(JobPosts)