from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from recruiter.company.schema import CompanyCreation

# Job Post Schema
class JobCreation(Schema):
    title : str
    description : str
    city : str
    country : str
    location_type : List[str]
    address : List[str] | None = None
    type : List[str]
    schedule : List[str]
    start_date : Optional[date] = None
    vacancy : int
    timeline : str
    salary_min : Optional[int] = None
    salary_max : Optional[int] = None
    salary_period : Optional[str] = None
    benefits : Optional[Union[List[str], Dict[str, Any]]] = None
    supplimental_pay : Optional[Union[List[str], Dict[str, Any]]] = None
    application_updations_email : Optional[Union[List[str], Dict[str, Any]]] = None
    resume_required : Optional[bool] = None
    end_date : Optional[date] = None
    skills : Optional[Union[List[str], Dict[str, Any]]] = None
    interview_rounds : Optional[Union[List[str], Dict[str, Any]]] = None
    professional_exp : Optional[float] = None
    total_experience : Optional[float] = None
    education : Optional[str] = None
    custom_qns : Optional[Union[List[str], Dict[str, Any]]] = None
    languages : Optional[Union[List[str], Dict[str, Any]]] = None
    work_location: Optional[Union[List[str], Dict[str, Any]]] = None
    commute : Optional[bool] = None
    relocate : Optional[bool] = None
    date_availablity : Optional[bool] = None
    gender : Optional[str] = None

JobData = create_schema(JobPosts)

class JobCompanyData(Schema):
    job_posts : JobData
    company_data : CompanyCreation