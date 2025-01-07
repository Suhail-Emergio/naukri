from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import date

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
    nationality : str
    gender : str
    total_experience_years : int
    total_experience_months : int

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

class LanguageData(Schema):
    id: Optional[int]
    language: str
    proficiency: str
    comfortability: str

class ProjectData(Schema):
    id: Optional[int]
    title: str
    client: str
    status: str
    started_on: str
    ended_on: Optional[str]
    details: str
    skills: List[str]

class CertificateData(Schema):
    id: Optional[int]
    title: str
    publication: str
    description: str
    published_on: date