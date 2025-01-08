from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from recruiter.company.schema import CompanyCreation

# Job Post Schema
class JobCreation(Schema):
    title : str
    description : str
    type : str
    category : str
    city : str
    country : str
    vacancy : int
    industry : str
    functional_area : str
    gender : Optional[str] = None
    nationality : Optional[str] = None
    experience_min : Optional[int] = None
    experience_max : Optional[int] = None
    candidate_location : Optional[List[str]] = None
    education : Optional[str] = None
    salary_min : Optional[int] = None
    salary_max : Optional[int] = None
    currency : Optional[str] = None
    skills : Optional[List[str]] = None
    custom_qns : Optional[List[str]] = None

JobData = create_schema(JobPosts)

class JobCompanyData(Schema):
    job_posts : JobData
    company_data : CompanyCreation