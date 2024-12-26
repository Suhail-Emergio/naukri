from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
job_actions_api = Router(tags=['job-actions'])

@job_actions_api.post("/apply", response={201: ApplyJobsData, 404: Message, 409: Message}, description="Apply for a job post")
async def apply_jobs(request, data: ApplyJobsCreation):
    data_dict = data.dict()
    if await JobPosts.objects.filter(id=data_dict['job_id']).aexists():
        job = await JobPosts.objects.aget(id=data_dict['job_id'])
        apply_job = await ApplyJobs.objects.acreate(user=request.auth, job=job)
        return 201, apply_job
    return 404, {"message": "Job not found"}

@job_actions_api.get("/apply", response={200: List[ApplyJobsData], 409: Message}, description="Retrieve all job posts a user applied")
async def applied_jobs(request):
    jobs = [i async for i in ApplyJobs.objects.filter(user=request.auth).order_by('-created_on')]
    return 200, jobs

@job_actions_api.post("/save", response={201: SavedJobsData, 404: Message, 409: Message}, description="Save/ Bookmark a job post if not already saved, if already saved remove it")
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
        return 201, save_job
    return 404, {"message": "Job not found"}

@job_actions_api.get("/save", response={200: List[SavedJobsData], 409: Message}, description="Retrieve all job posts a user applied")
async def saved_jobs(request):
    jobs = [i async for i in SaveJobs.objects.filter(user=request.auth).order_by('-created_on')]
    return 200, jobs

# async def invited_jobs(request):
# async def search_jobs(request):
# async def filter_jobs(request):