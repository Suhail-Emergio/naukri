from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

# Personal Schema
class PersonalCreation(Schema):
    intro : str
    city : str
    state : str
    cv : Optional[str] = None
    skills : List[str]
    prefered_salary_pa : int
    prefered_work_loc : str

PersonalData = create_schema(Personal)

# Employment Schema
class EmploymentCreation(Schema):
    employed : bool
    experiance: int
    job_title: str
    company_name: str
    duration: int
    ctc: int
    notice_pd: int
    department: str
    job_role: str
    role_category: str

EmploymentData = create_schema(Employment)

# Professional Schema
class ProfessionalCreation(Schema):
    student: bool = False
    education: str
    course: str
    type_course: str
    specialisation: str
    university: str
    starting_yr: int
    ending_yr: int
    grade: int

ProfessionalData = create_schema(Professional)