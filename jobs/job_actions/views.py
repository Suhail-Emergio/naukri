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
from seeker.details.models import *
from datetime import datetime, timedelta

User = get_user_model()
job_actions_api = Router(tags=['job-actions'])

#################################  V I E W  J O B S  #################################
@job_actions_api.get("/view_jobs", response={201: Message, 404: Message, 409: Message}, description="Updation on viewing a job post")
async def view_jobs(request, job_id: int):
    if await JobPosts.objects.filter(id = job_id).aexists():
        job = await JobPosts.objects.aget(id=job_id)
        job.views += 1
        return 201, {"message": "Updated succesfully"}
    return 404, {"message": "Job not found"}

#################################  A P P L Y  J O B S  #################################
@job_actions_api.post("/apply", response={201: Message, 404: Message, 405: Message, 409: Message}, description="Apply for a job post")
async def apply_jobs(request, data: ApplyJobsCreation):
    data_dict = data.dict()
    if await JobPosts.objects.filter(id=data_dict['job_id']).aexists():
        job = await JobPosts.objects.aget(id=data_dict['job_id'])
        custom_qns = data_dict['custom_qns'] if data_dict['custom_qns'] else None
        invited = False
        if await ApplyJobs.objects.filter(user=request.auth, job=job).aexists():
            return 405, {"message": "Already applied"}
        if await InviteCandidate.objects.filter(candidate__user=request.auth, job=job).aexists():
            invited = True
            invite = await InviteCandidate.objects.aget(candidate__user=request.auth, job=job)
            invite.status = "applied"
            await invite.asave()
        apply_job = await ApplyJobs.objects.acreate(user=request.auth, job=job, custom_qns=custom_qns, invited=invited)
        return 201, {"message": "Successfully added"}
    return 404, {"message": "Job not found"}

@job_actions_api.get("/applied_jobs", response={200: List[ApplyJobsData], 409: Message}, description="Retrieve all job posts a user applied")
async def applied_jobs(request):
    jobs = []
    async for i in ApplyJobs.objects.filter(user=request.auth).order_by('-created_on'):
        job = await sync_to_async(lambda: i.job)()
        id = await sync_to_async(lambda: i.id)()
        created_on = await sync_to_async(lambda: i.created_on)()
        custom_qns = await sync_to_async(lambda: i.custom_qns)()
        status = await sync_to_async(lambda: i.status)()
        viewed = await sync_to_async(lambda: i.viewed)()
        created_on = await sync_to_async(lambda: i.created_on)()
        company = await sync_to_async(lambda: job.company)()
        jobs.append({"job": {"job_posts": job, "company_data": company}, "id": id, "custom_qns": custom_qns, "status": status, "viewed": viewed, "created_on": created_on})
    return 200, jobs

#################################  A P P L I C A T I O N S  #################################
@job_actions_api.get("/job_applications", response={200: List[ApplyCandidatesData], 404: Message, 409: Message}, description="Retrieve all job applications for a company for all jobs/ for a job post")
async def job_applications(request, 
        job_id: Optional[int] = None,
        location : Optional[str] = None,
        gender: Optional[str] = None,
        experiance_range: Optional[str] = None,
        skills: List[str] = Query(None, description="List of skills"),
        immediate_joining: Optional[bool] = None,
    ):
    user = request.auth
    query = ()
    if job_id:
        if await JobPosts.objects.filter(id=job_id).aexists():
            query = Q(job__id=job_id)
        else:
            return 404, {"message": "Job not found"}
    else:
        query = Q(job__company__user=user)
    if location:
        # locations = await sync_to_async(Personal.objects.filter)(city=location)
        users = []
        async for i in Personal.objects.filter(city=location):
            users.append(await sync_to_async(lambda: i.user.id)())
        query &= Q(user__in=[users])
        # query &= Q(user__personal__city=location)
    if gender:
        query &= Q(user__personal__gender=gender)
    if experiance_range:
        exp_range = experiance_range.split("-")
        query &= Q(user__personal__total_experience_years__gte=exp_range[0]) & Q(user__personal__total_experience_years__lte=exp_range[1])
    if skills:
        query &= Q(user__personal__skills__in=skills)
    if immediate_joining:
        query &= Q(user__personal__immediate_joiner=immediate_joining)
    applications = []
    async for i in ApplyJobs.objects.filter(query).order_by('-created_on'):
        candidate = await sync_to_async(lambda: i.user)()
        candidates = []
        if not await Personal.objects.filter(user=candidate).aexists():
            continue
        personal = await Personal.objects.aget(user=candidate)
        employment = None
        if await Employment.objects.filter(user=candidate).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate).order_by('-id')]
        job = await sync_to_async(lambda: i.job)()
        id = await sync_to_async(lambda: i.id)()
        created_on = await sync_to_async(lambda: i.created_on)()
        viewed = await sync_to_async(lambda: i.viewed)()
        status = await sync_to_async(lambda: i.status)()
        custom_qns = await sync_to_async(lambda: i.custom_qns)()
        applied_jobs = []
        async for i in ApplyJobs.objects.filter(user=candidate, job__company__user=user):
            applied_jobs.append(await sync_to_async(lambda: i.job)())
        matching_skills = []
        job_skills = await sync_to_async(lambda: job.skills)()
        individual_skills = await sync_to_async(lambda: personal.skills)()
        for i in individual_skills:
            if i in job_skills:
                matching_skills.append(i)
        applications.append({
            "id": id,
            'job': job,
            'applied_jobs': applied_jobs,
            "candidate": {"personal": {"personal": personal, "user": candidate}, "employment": employment, "qualification": qualification},
            "custom_qns": custom_qns,
            "status": status,
            "viewed": viewed,
            "created_on": created_on,
            "matching_skills": matching_skills
        })
    return 200, applications

@job_actions_api.patch("/update_job_applications", response={200: Message, 409: Message}, description="Update view on job application after recruiter views an application")
async def update_job_applications(request, applied_id: int):
    if await ApplyJobs.objects.filter(id=applied_id).aexists():
        applied = await ApplyJobs.objects.aget(id=applied_id)
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

            current_date = datetime.now()
            if freshness:
                diff = current_date - timedelta(days=freshness)
                queries &= Q(created_on__gte=diff)

        jobs = [i async for i in JobPosts.objects.filter(queries).exclude(active=False).order_by('-created_on')]
        job_company_data = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
        return 200, job_company_data
    return 409, {"message": "Please provide specialization or query"}