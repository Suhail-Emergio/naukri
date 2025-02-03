from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q
from recruiter.company.models import CompanyDetails
from seeker.seeker_actions.models import BlockedCompanies

User = get_user_model()
jobs_api = Router(tags=['jobs'])

#################################  J O B  P O S T S  #################################
@jobs_api.post("/", response={201: JobData, 400: Message, 401: Message, 409:Message}, description="Job data creation")
async def job(request, data: JobCreation):
    if request.auth.subscribed:
        # Data validation
        if data.experience_min and data.experience_max and data.experience_min > data.experience_max:
            return 400, {"message": "Minimum experience cannot be greater than maximum"}
        if data.salary_min and data.salary_max and data.salary_min > data.salary_max:
            return 400, {"message": "Minimum salary cannot be greater than maximum"}
        if request.auth.role == "recruiter":
            if not await CompanyDetails.objects.filter(user=request.auth).aexists():
                return 400, {"message": "Create company details first"}
            company = await CompanyDetails.objects.aget(user=request.auth)
            job = await JobPosts.objects.acreate(company=company, **data.dict())
            return 201, job
        return 409, {"message": "Not Authorised"}
    return 401, {"message": "No subscriptions taken"}

@jobs_api.patch("/edit", response={200: JobData, 404: Message, 409: Message}, description="Job posts data update")
async def update_jobpost(request, data: PatchDict[JobData]):
    if await JobPosts.objects.filter(id=data['id']).aexists():
        job = await JobPosts.objects.aget(id=data['id'])
        for attr, value in data.items():
            setattr(job, attr, value)
        await job.asave()
        return 200, job
    return 404, {"message": "Job data not found"}

@jobs_api.get("/", response={200: List[JobData], 409: Message}, description="Job data passing of logged user")
async def jobs(request):
    job = [i async for i in JobPosts.objects.filter(company__user=request.auth)]
    return 200, job

@jobs_api.delete("/delete_job", response={200: List[JobData], 404: Message, 409: Message}, description="Job data passing of logged user")
async def delete_job(request, id: str):
    if await JobPosts.objects.filter(id=id).aexists():
        job = await JobPosts.objects.aget(id=id)
        await job.adelete()
    return 404, {"message": "Job data not found"}

@jobs_api.get("/all_jobs", response={200: List[JobCompanyData], 409: Message}, description="Job data passing of all posts with respective company details")
async def all_jobs(request):
    excludable_data = []
    if await BlockedCompanies.objects.filter(user=request.auth).aexists():
        excludable_data = [i.company for i in await BlockedCompanies.objects.filter(user=request.auth)]
    jobs = [i async for i in JobPosts.objects.all().exclude(company__in=excludable_data, active=False)]
    job_company_data = []
    for job in jobs:
        company_details = await CompanyDetails.objects.aget(id=job.company_id)
        job_company_data.append({"job_posts": job, "company_data": company_details})
    return 200, job_company_data