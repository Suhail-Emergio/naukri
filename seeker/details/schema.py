from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import date
from user.schema import UserData

# Personal Schema
class PersonalCreation(Schema):
    intro : str
    city : str
    state : str
    employed : bool
    skills : Union[List[str], Dict[str, Any]]|None=True
    prefered_salary_pa : int
    prefered_work_loc : Union[List[str], Dict[str, Any]]
    nationality : str
    gender : str
    total_experience_years : int
    total_experience_months : int
    address: Union[List[str], Dict[str, Any]]
    differently_abled: bool
    dob: date
    work_availability: bool | None = True

class PersonalData(Schema):
    id: int
    intro : str
    city : str
    state : str
    employed : bool
    cv : Optional[str] = None
    profile_image : Optional[str] = None
    skills : Union[List[str], Dict[str, Any]]
    prefered_salary_pa : int
    prefered_work_loc : Union[List[str], Dict[str, Any]]
    nationality : str
    gender : str
    total_experience_years : int
    total_experience_months : int
    address: Union[List[str], Dict[str, Any]] | None = None
    differently_abled: bool | None = None
    dob: date | None = None
    work_availability: bool | None = True
    immediate_joiner : bool

class PersonalSchema(Schema):
    personal: PersonalData
    user: UserData

# Employment Schema
class EmploymentCreation(Schema):
    experiance: int
    job_title: str
    company_name: str
    duration: int
    ctc: int
    notice_pd: int
    department: str
    industry: str
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
    job_type: List[str]
    employment_type: List[str]
    job_shift: List[str]
    job_role: Union[List[str], Dict[str, Any]]
    pref_salary: int
    job_location: Union[List[str], Dict[str, Any]]

PreferenceData = create_schema(Preference)

class LanguageData(Schema):
    id: Optional[int] = None
    language: str
    proficiency: str
    comfortability: str

class ProjectData(Schema):
    id: Optional[int] = None
    title: str
    client: str
    status: str
    started_on: str
    ended_on: Optional[str]
    details: str
    skills: Union[List[str], Dict[str, Any]]

class CertificateData(Schema):
    id: Optional[int] = None
    title: str
    publication: str
    description: str
    published_on: str

class CountData(Schema):
    models_with_empty_fields: Union[List[str], Dict[str, Any]]
    empty_models: Union[List[str], Dict[str, Any]]
    profile_completion_percentage: float
    applied_jobs_count: int
    jobs_viewed_count: int
    interview_scheduled_count: int

# Notification Preference Schema
class NotificationPreferencePatch(Schema):
    recommendations: Literal["daily", "weekly", "ban"]
    alerts: Literal["daily", "weekly", "ban"]
    mobile_notifications: bool
    messages_recruiter: Literal["immediately", "ban"]
    applications: Literal["daily", "ban"]
    promotions: Literal["daily", "ban"]

NotifactionPreferenceData = create_schema(NotificationPreference)