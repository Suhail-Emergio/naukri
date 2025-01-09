from ninja import Router, Query
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from user.schema import *
from django.db.models import Q
from jobs.jobposts.schema import JobCompanyData
from jobs.jobposts.models import JobPosts
from recruiter.company.models import CompanyDetails
from recruiter.recruiter_actions.models import InviteCandidate
from asgiref.sync import sync_to_async

User = get_user_model()
job_actions_api = Router(tags=['job-actions'])

#################################  A P P L Y  J O B S  #################################
@job_actions_api.post("/apply", response={201: Message, 404: Message, 409: Message}, description="Apply for a job post")
async def apply_jobs(request, data: ApplyJobsCreation):
    data_dict = data.dict()
    if await JobPosts.objects.filter(id=data_dict['job_id']).aexists():
        job = await JobPosts.objects.aget(id=data_dict['job_id'])
        custom_qns = data_dict['custom_qns'] if data_dict['custom_qns'] else None
        invited = False
        if await InviteCandidate.objects.filter(candidate__user=request.auth, job=job).aexists():
            invited = True
            invite = await InviteCandidate.objects.aget(candidate__user=request.auth, job=job)
            invite.interested = True
            await invite.asave()
        apply_job = await ApplyJobs.objects.acreate(user=request.auth, job=job, custom_qns=custom_qns, invited=invited)
        return 201, {"message": "Successfully added"}
    return 404, {"message": "Job not found"}

@job_actions_api.get("/applied_jobs", response={200: List[ApplyJobsData], 409: Message}, description="Retrieve all job posts a user applied")
async def applied_jobs(request):
    jobs = []
    async for i in ApplyJobs.objects.filter(user=request.auth).order_by('-created_on'):
        job = await sync_to_async(lambda: i.job)()
        created_on = await sync_to_async(lambda: i.created_on)()
        custom_qns = await sync_to_async(lambda: i.custom_qns)()
        status = await sync_to_async(lambda: i.status)()
        viewed = await sync_to_async(lambda: i.viewed)()
        created_on = await sync_to_async(lambda: i.created_on)()
        company = await sync_to_async(lambda: job.company)()
        jobs.append({"job": {"job_posts": job, "company_data": company}, "custom_qns": custom_qns, "status": status, "viewed": viewed, "created_on": created_on})
    return 200, jobs

#################################  A P P L I C A T I O N S  #################################
@job_actions_api.get("/job_applications", response={200: List[ApplyJobsData], 409: Message}, description="Retrieve all job applications for a company for a job post")
async def job_applications(request, job_id: int):
    if await JobPosts.objects.filter(id=job_id).aexists():
        jobs = [i async for i in ApplyJobs.objects.filter(job__id=job_id).order_by('-created_on')]
        return 200, jobs
    return 404, {"message": "Job not found"}

@job_actions_api.get("/view_job_applications", response={200: Message, 409: Message}, description="Update view on job application after recruiter views an application")
async def view_job_applications(request, applied_id: int):
    if await ApplyJobs.objects.filter(id=applied_id).aexists():
        applied = await ApplyJobs.objects.aget(job__id=applied_id)
        applied.viewed = True
        return 200, {"message": "Updated successfully"}
    return 404, {"message": "Applied job not found"}

#################################  S A V E /  B O O K M A R K  J O B S  #################################
@job_actions_api.post("/save", response={201: Message, 200: Message, 404: Message, 409: Message}, description="Save/ Bookmark a job post if not already saved, if already saved remove it")
async def save_jobs(request, data: SavedJobsCreation):
    data_dict = data.dict()
    if await JobPosts.objects.filter(id=data_dict['job_id']).aexists():
        job = await JobPosts.objects.aget(id=data_dict['job_id'])

        ## Delete saved job if already saved
        if await SaveJobs.objects.filter(user=request.auth, job=job).aexists():
            await SaveJobs.objects.filter(user=request.auth, job=job).adelete()
            return 200, {"message": "Saved job deleted"}

        ## Save job
        save_job = await SaveJobs.objects.acreate(user=request.auth, job=job)
        return 201, {"message": "Successfully created"}
    return 404, {"message": "Job not found"}

@job_actions_api.get("/save", response={200: List[SavedJobsData], 409: Message}, description="Retrieve all job posts a user applied")
async def saved_jobs(request):
    jobs = []
    async for i in SaveJobs.objects.filter(user=request.auth).order_by('-created_on'):
        job = await sync_to_async(lambda: i.job)()
        created_on = await sync_to_async(lambda: i.created_on)()
        company = await sync_to_async(lambda: job.company)()
        jobs.append({"job": {"job_posts": job, "company_data": company}, "created_on": created_on})
    return 200, jobs

#################################  S E A R C H  &  F I L T E R  J O B S  #################################
@job_actions_api.get("/search", response={200: List[JobCompanyData], 409: Message}, description="Retrieve all job posts a user searched & filtered")
async def search_jobs(request, 
        specialization: str = None, 
        query: str = None, 
        filter: bool = False, 
        job_category: str = None,
        job_type: str = None,
        city: str = None,
        salary_min: int = None,
        salary_max: int = None,
        experience_min : int = None,
        experience_max : int = None,
        freshness: int = None
    ):
    if specialization or query:
        queries = Q()

        # Querying jobs based on specialization\ query
        if specialization and query:
            queries &= (Q(industry__icontains=specialization) | Q(functional_area__icontains=specialization)) & Q(title__icontains=query)
        elif specialization:
            queries &= Q(industry__icontains=specialization) | Q(functional_area__icontains=specialization)
        elif query:
            queries &= Q(title__icontains=query)

        # Filtering jobs based on filter data from above query
        if filter:
            queries &= Q(category=job_category) if job_category else Q()
            queries &= Q(type=job_type) if job_type else Q()
            queries &= Q(city=city) if city else Q()
            queries &= Q(salary_min__gte=salary_min) if salary_min is not None else Q()
            queries &= Q(salary_max__lte=salary_max) if salary_max is not None else Q()
            queries &= Q(experience_min__gte=experience_min) if experience_min is not None else Q()
            queries &= Q(experience_max__lte=experience_max) if experience_max is not None else Q()
            queries &= Q(created_on__gte=freshness) if freshness is not None else Q()

        jobs = [i async for i in JobPosts.objects.filter(queries).order_by('-created_on')]
        job_company_data = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
        return 200, job_company_data
    return 409, {"message": "Please provide specialization or query"}