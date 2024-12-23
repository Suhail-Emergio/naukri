from ninja import Router
from django.contrib.auth import get_user_model
from jobposts.schema import *
from typing import *
from jobposts.models import *
from user.schema import *
from django.db.models import Q
from seeker.details.models import Preference, Personal, Emjployment

User = get_user_model()
based_jobs_api = Router(tags=['basedjobs'])

@based_jobs_api.get("/prefered_jobs", response={200: List[JobCompanyData], 404: Message, 409: Message}, description="Retrieve all job posts with respective company details based on user preferences")
async def prefered_jobs(request):
    user = request.auth
    preferences = await Preference.objects.filter(user=user).afirst()
    if not preferences:
        return 404, {"message": "User preferences not found"}

    jobs = [i async for i in JobPosts.objects.filter(
        Q(location__in=preferences.locations) |
        Q(job_type__in=preferences.job_types) |
        Q(industry__in=preferences.industries)
    )]

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
    if personal:
        if personal.employed and employment:
            query = Q(title=employment.job_title) | Q(industry=employment.industry) | Q(functional_area=employment.functional_area)
        if personal.state:
            query |= Q(address__state = personal.state)
        jobs = [i async for i in JobPosts.objects.filter(query)]
        job_company_data = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
        return 200, job_company_data
    return 404, {"message": "User profile data not found"}