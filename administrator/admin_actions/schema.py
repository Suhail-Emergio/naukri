from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *
from datetime import timedelta
from jobs.job_actions.schema import ApplyCandidatesData
from recruiter.recruiter_actions.schema import SeekerData
from jobs.jobposts.schema import JobCompanyData, JobData
from datetime import datetime
from common_actions.models import Notification

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
    audience: str
    duration: timedelta

BannerData = create_schema(Banner)

class ApplicationStats(Schema):
    applications: List[ApplyCandidatesData]
    views: int
    candidates: int
    shortlisted: int
    rejected: int

class AdminCompany(Schema):
    name: str
    about : str
    website : str
    functional_area : str
    address : Union[List[str], Dict[str, Any]]
    city : str
    state : str
    postal_code : str
    logo: str | None
    id: int
    jobs: List[JobData]

class AllSubsData(Schema):
    id: int
    seeker: Optional[List[SeekerData]]
    plan: PlanData
    remaining_posts: int
    transaction_id: str
    subscribed_on: str

class AllJobsData(Schema):
    job: JobCompanyData
    remaining_vacancy: int
    company_name: str
    company_logo: str | None

class AllNotifications(Schema):
    id: int
    title: str
    description: str
    image: str | None
    url: str | None
    created_on: str
    user: List[str]
    read_by: List[str]

class AllUsers(Schema):
    id: int
    name: str
    username: str

class AdminCandidatesData(Schema):
    id: int
    job: JobData
    candidate: SeekerData
    company: str
    status: str
    viewed: bool
    created_on: datetime

NotiData = create_schema(Notification)