from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
jobs_api = Router(tags=['jobs'])

@jobs_api.post("/", response={201: JobData, 400: Message, 401: Message, 409:Message}, description="Job data creation")
async def job(request, data: JobCreation):
    data_dict = data.dict()

    # Data validation
    if data.experience_min and data.experience_max and data.experience_min > data.experience_max:
        return 400, {"message": "Minimum experience cannot be greater than maximum"}
    if data.salary_min and data.salary_max and data.salary_min > data.salary_max:
        return 400, {"message": "Minimum salary cannot be greater than maximum"}

    if request.auth.role == "recruiter":
        data_dict['user'] = request.auth
        job = await JobPosts.objects.acreate(**data_dict)
        return 201, job
    return 401, {"message": "Not Authorised"}

@jobs_api.get("/", response={200: List[JobData], 409: Message}, description="Job data passing of logged user")
async def jobs(request):
    job = [i async for i in JobPosts.objects.filter(user=request.auth)]
    return 200, job

@jobs_api.get("/all_jobs", response={200: List[JobData], 409: Message}, description="Job data passing of all posts")
async def all_jobs(request):
    job = [i async for i in JobPosts.objects.all()]
    return 200, job