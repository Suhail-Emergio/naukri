from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

# Personal Schema
class PersonalCreation(Schema):
    intro : str
    city : str
    state : str
    employed : bool
    cv : Optional[str] = None
    skills : List[str]
    prefered_salary_pa : int
    prefered_work_loc : str

PersonalData = create_schema(Personal)

# Employment Schema
class EmploymentCreation(Schema):
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

# Qualification Schema
class QualificationCreation(Schema):
    student: bool = False
    education: str
    course: str
    type_course: str
    specialisation: str
    university: str
    starting_yr: int
    ending_yr: int
    grade: int

QualificationData = create_schema(Qualification)

# Preference Schema
class PreferenceCreation(Schema):
    job_type: str
    employment_type: str
    job_shift: str
    job_role: List[str]
    pref_salary: int
    job_location: List[str]

PreferenceData = create_schema(Preference)