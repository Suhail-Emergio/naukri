from ninja import Schema
from typing import *
from ninja.orm import create_schema
from seeker.details.schema import *
from .models import *

class SearchCriteria(Schema):
    keywords: Optional[List[str]] = None
    experience_year: Optional[int] = None
    experience_month: Optional[int] = None
    current_loc: Optional[str] = None
    nationality: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    gender: Optional[str] = None
    additional: Optional[str] = None

class SeekerData(Schema):
    personal : PersonalData
    employment: Optional[EmploymentData] = None
    qualification: Optional[QualificationData] = None