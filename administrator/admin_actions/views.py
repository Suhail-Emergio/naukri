from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *
from jobs.jobposts.schema import JobCompanyData
from ninja.pagination import paginate
from jobs.jobposts.models import JobPosts
from jobs.job_actions.schema import ApplyJobs, ApplyCandidatesData

User = get_user_model()
admin_api = Router(tags=['admin'])

#################################  J O B S  #################################
@admin_api.get("/all_jobs", response={201: List[JobCompanyData], 409:Message}, description="Fetch all jobs")
async def all_jobs(request, order: str = 'active'):
    user = request.auth
    if user.is_superuser:
        jobs = [i async for i in JobPosts.objects.all().order_by(f'-{order}')]
        job_company_data = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            job_company_data.append({"job_posts": job, "company_data": company_details})
        return 200, job_company_data
    return 409, {"message" : "You are not authorized"}

@admin_api.get("/job_application", response={200: ApplicationStats, 409:Message}, description="Fetch all applications for a job")
@paginate
async def all_jobs(request,  job_id: int, order: str = 'active'):
    user = request.auth
    if user.is_superuser:
        applications = []
        views = 0
        candidates = 0
        shortlisted = 0
        rejected = 0
        async for i in ApplyJobs.objects.filter(job__id=job_id).order_by(f'-{order}'):
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
            applications.append({
                "id": id,
                'job': job,
                'applied_jobs': applied_jobs,
                "candidate": {"personal": {"personal": personal, "user": candidate}, "employment": employment, "qualification": qualification},
                "custom_qns": custom_qns,
                "status": status,
                "viewed": viewed,
                "created_on": created_on,
            })
            if i.status == "shortlisted":
                shortlisted += 1 
            elif i.status == "rejected":
                rejected += 1 
            else:
                candidates += 1
        return 200, {
            "applications": applications,
            "views": 0,
            "candidates": candidates,
            "shortlisted": shortlisted,
            "rejected": rejected
        }
    return 409, {"message" : "You are not authorized"}

#################################  J O B S  #################################
@admin_api.get("/all_applications", response={201: List[ApplyCandidatesData], 409:Message}, description="Fetch all job applications")
@paginate
async def all_applications(request, order: str = 'active'):
    user = request.auth
    if user.is_superuser:
        applications = []
        async for i in ApplyJobs.objects.all().order_by(f'-{order}'):
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
            applications.append({
                "id": id,
                'job': job,
                'applied_jobs': applied_jobs,
                "candidate": {"personal": {"personal": personal, "user": candidate}, "employment": employment, "qualification": qualification},
                "custom_qns": custom_qns,
                "status": status,
                "viewed": viewed,
                "created_on": created_on,
            })
        return 200, applications
    return 409, {"message" : "You are not authorized"}

#################################  P L A N S  #################################
@admin_api.post("/create_plans", response={201: Message, 409:Message}, description="Plan creations")
async def plan_creation(request, data: PlanCreation):
    user = request.auth
    if user.is_superuser:
        plan = await Plans.objects.acreate(**data.dict())
        await plan.asave()
        return 201, {"message" : "Plan created successfuly"}
    return 409, {"message" : "You are not authorized to create plans"}

@admin_api.get("/plans", response={201: List[PlanData], 409:Message}, description="Plan details")
async def plans(request):
    user = request.auth
    if user.is_superuser:
        plan = [i async for i in Plans.objects.all()]
        return 201, plan
    return 409, {"message" : "You are not authorized to create plans"}


@admin_api.get("/update_plans", response={201: Message, 409:Message}, description="Plan details")
async def update_plans(request, data: PatchDict[PlanCreation]):
    user = request.auth
    if user.is_superuser:
        if await Plans.objects.filter(id=data.id).aexists():
            plan = await Plans.objects.aget(id=data.id)
            for key, value in data.items():
                setattr(plan, key, value)
            await plan.asave()
            return 201, {"message" : "Plan updated successfuly"}
        return 409, {"message" : "Plan doesnot exists"}

@admin_api.get("/delete_plans", response={201: Message, 404: Message, 409:Message}, description="Plan details")
async def delete_plans(request, id: int):
    user = request.auth
    if user.is_superuser:
        if await Plans.objects.filter(id=id).aexists():
            plan = await Plans.objects.aget(id=id)
            await plan.adelete()
            return 201, {"message" : "Plan deleted successfuly"}
        return 404, {"message" : "Plan doesnot exists"}
    return 409, {"message" : "You are not authorized to delete plans"}

#################################  B A N N E R S  #################################
@admin_api.post("/create_banners", response={201: Message, 409:Message}, description="Banner creations")
async def banner_creation(request, data: BannerCreation):
    user = request.auth
    if user.is_superuser:
        banner = await Banner.objects.acreate(**data.dict())
        await banner.asave()
        return 201, {"message" : "Banner created successfuly"}
    return 409, {"message" : "You are not authorized to create banners"}

@admin_api.get("/banners", response={201: List[BannerData], 409:Message}, description="Banner details")
async def banners(request):
    user = request.auth
    if user.is_superuser:
        banner = [i async for i in Banner.objects.all()]
        return 201, banner
    return 409, {"message" : "You are not authorized to create banners"}


@admin_api.get("/update_banner", response={201: Message, 409:Message}, description="Banner updations")
async def update_banner(request, data: PatchDict[PlanCreation]):
    user = request.auth
    if user.is_superuser:
        if await Banner.objects.filter(id=data.id).aexists():
            banner = await Banner.objects.aget(id=data.id)
            for key, value in data.items():
                setattr(banner, key, value)
            await banner.asave()
            return 201, {"message" : "banner updated successfuly"}
        return 409, {"message" : "banner doesnot exists"}
    return 409, {"message" : "You are not authorized to delete banners"}

@admin_api.get("/delete_banners", response={201: Message, 404: Message, 409:Message}, description="banner details")
async def delete_banners(request, id: int):
    user = request.auth
    if user.is_superuser:
        if await Banner.objects.filter(id=id).aexists():
            banner = await Banner.objects.aget(id=id)
            await banner.adelete()
            return 201, {"message" : "banner deleted successfuly"}
        return 404, {"message" : "banner doesnot exists"}
    return 409, {"message" : "You are not authorized to delete banners"}