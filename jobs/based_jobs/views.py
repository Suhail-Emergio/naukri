from ninja import Router
from django.contrib.auth import get_user_model
from jobs.jobposts.schema import *
from typing import *
from jobs.jobposts.models import *
from user.schema import *
from django.db.models import Q
from seeker.details.models import Preference, Personal, Employment
from recruiter.company.models import CompanyDetails
from common_actions.models import Subscription
from seeker.seeker_actions.models import BlockedCompanies
from asgiref.sync import sync_to_async

User = get_user_model()
based_jobs_api = Router(tags=['based-jobs'])

#################################  J O B S  B A S E D  O N  D I F F  I N F O S  #################################
@based_jobs_api.get("/prefered_jobs", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all job posts with respective company details based on user preferences")
async def prefered_jobs(request):
    user = request.auth
    preferences = await Preference.objects.filter(user=user).afirst()
    if not preferences:
        return 404, {"message": "User preferences not found"}
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    jobs = [i async for i in JobPosts.objects.filter(
        Q(type__in=preferences.job_type) |
        Q(city__in=preferences.job_location) |
        Q(type__in=preferences.employment_type) |
        Q(type__in=preferences.employment_type) |
        Q(title__icontains=preferences.job_role)
    ).exclude(active=False, company__in=excludable_data)]
    job_company_data = []
    for job in jobs:
        company_details = await CompanyDetails.objects.aget(id=job.company_id)
        job_company_data.append({"job_posts": job, "company_data": company_details})
    return 200, job_company_data

@based_jobs_api.get("/profile_based", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all job posts based on user profile data")
async def profile_based_jobs(request):
    user = request.auth
    personal = await Personal.objects.filter(user=user).afirst()
    employment = await Employment.objects.filter(user=user).afirst()
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    if personal:
        query = Q()
        if personal.employed and employment:
            query = Q(title=employment.job_title) | Q(industry=employment.department) | Q(functional_area=employment.job_role)
        query |= Q(city = personal.prefered_work_loc) | Q(country = personal.prefered_work_loc)
        jobs = [i async for i in JobPosts.objects.filter(query).exclude(active=False)]
        job_company_data = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
        return 200, job_company_data
    return 404, {"message": "User profile data not found"}

@based_jobs_api.get("/category_based", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all job posts based on category")
async def category_based_jobs(request, category: str = "remote"):
    if not category:
        return 409, {"message": "Category not provided"}
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    jobs = [i async for i in JobPosts.objects.filter(category=category, active=False).exclude(company__in=excludable_data)]
    job_company_data = []
    for job in jobs:
        company_details = await CompanyDetails.objects.aget(id=job.company_id)
        job_company_data.append({"job_posts": job, "company_data": company_details})
    return 200, job_company_data

@based_jobs_api.get("/similar_jobs", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all job posts based on category")
async def similar_jobs(request, job_id: str):
    if not job_id:
        return 409, {"message": "Job id not provided"}
    job = await JobPosts.objects.aget(id=job_id)
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    jobs = [i async for i in JobPosts.objects.filter(Q(title__icontains=job.title) | Q(type=job.type) | Q(industry=job.industry)).exclude(id=job_id, active=False, company__in=excludable_data)]
    job_company_data = []
    for job in jobs:
        company = await sync_to_async(lambda: job.company)()
        job_company_data.append({"job_posts": job, "company_data": company_details})
    return 200, job_company_data

@based_jobs_api.get("/featured_jobs", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all featured job posts")
async def featured_jobs(request):
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    jobs = [i async for i in JobPosts.objects.filter(category=category, company__user__subscribed=True).exclude(active=False, company__in=excludable_data).order_by('-id')]
    job_company_data = []
    for job in jobs:
        company = await sync_to_async(lambda: job.company)()
        user = await sync_to_async(lambda: company.user)()
        if await Subscription.objects.filter(user=user, plan__feature=True).aexists():
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
    return 200, job_company_data