from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import timedelta
from jobs.job_actions.schema import ApplyCandidatesData
from seeker.details.schema import SeekerData
from jobs.jobposts.schema import JobCompanyData

class PlanCreation(Schema):
    title: str
    description: Dict[str, str]
    posts: int
    duration: timedelta
    audience: str
    resdex: bool = False
    rate: int
    feature: bool = False

PlanData = create_schema(Plans)

class BannerCreation(Schema):
    image: str

BannerData = create_schema(Banner)

class ApplicationStats(Schema):
    applications: List[ApplyCandidatesData]
    views: int
    candidates: int
    shortlisted: int
    rejected: int

class AdminCompany(Schema):
    about : str
    website : str
    functional_area : str
    address : Union[List[str], Dict[str, Any]]
    city : str
    country : str
    postal_code : str
    contact_name : str
    contact_land_number : str
    contact_mobile_number : str
    designation : str
    logo: str | None
    id: int

class AllSubsData(Schema):
    id: int
    seeker: SeekerData
    plan: PlanData
    remaining_posts: int
    transaction_id: str
    subscribed_on: str

class AllJobsData(Schema):
    job: JobCompanyData
    remaining_vacancy: int