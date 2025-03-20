from ninja import Router, PatchDict, File, UploadedFile
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *
from ninja.pagination import paginate
from jobs.jobposts.models import JobPosts
from jobs.job_actions.schema import ApplyJobs, ApplyCandidatesData
from recruiter.company.schema import CompanyDetails, CompanyData
from seeker.details.schema import Personal, Qualification, Employment
from recruiter.recruiter_actions.schema import SeekerData
from common_actions.models import Subscription
from common_actions.schema import NotificationCreation, Notification
from datetime import date, timedelta
from django.db.models import Count, Case, When, DateField
from django.db.models.functions import Cast

User = get_user_model()
admin_api = Router(tags=['admin'])

#################################  J O B S  #################################
@admin_api.get("/all_jobs", response={200: List[AllJobsData], 409:Message}, description="Fetch all jobs")
@paginate
async def all_jobs(request, order: str = 'active'):
    user = request.auth
    if user.is_superuser:
        jobs = [i async for i in JobPosts.objects.all().order_by(f'-{order}')]
        all_job = []
        for job in jobs:
            company_details = await CompanyDetails.objects.aget(id=job.company_id)
            company_name = await sync_to_async(lambda: company_details.name)()
            company_logo = await sync_to_async(lambda: company_details.logo)()
            vacancy = await sync_to_async(lambda: job.vacancy)()
            count = await ApplyJobs.objects.filter(job=job).acount()
            remaining_vacancy = vacancy - count
            all_job.append({"job": {"job_posts": job, "company_data": company_details}, "remaining_vacancy": remaining_vacancy, "company_name": company_name, "company_logo": company_logo})
        return all_job
    return {"message" : "You are not authorized"}

@admin_api.get("/job_post_application", response={200: ApplicationStats, 409:Message}, description="Fetch all applications for a job")
# @paginate
def job_post_application(request, job_id: int):
    user = request.auth
    if user.is_superuser:
        applications = []
        views = 0
        candidates = 0
        shortlisted = 0
        rejected = 0
        for i in ApplyJobs.objects.filter(job__id=job_id):
            if not Personal.objects.filter(user=i.user).exists():
                continue
            personal = Personal.objects.get(user=i.user)
            employment = None
            if Employment.objects.filter(user=i.user).exists():
                employment = Employment.objects.filter(user=i.user).order_by('-id')
            qualification = None
            if Qualification.objects.filter(user=i.user).exists():
                qualification = Qualification.objects.filter(user=i.user).order_by('-id')
            applied_jobs = []
            for i in ApplyJobs.objects.filter(user=i.user, job__company__user=user):
                applied_jobs.append(i.job)
            applications.append({
                "id": i.id,
                'job': i.job,
                'applied_jobs': applied_jobs,
                "candidate": {"personal": {"personal": personal, "user": i.user}, "employment": employment, "qualification": qualification},
                "custom_qns": i.custom_qns,
                "status": i.status,
                "viewed": i.viewed,
                "created_on": i.created_on,
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
    return {"message" : "You are not authorized"}

@admin_api.get("/job_post_application_leads", description="Fetch all leads for a job post date wisw")
def job_post_application_leads(request, job_id: int):
    user = request.auth
    if user.is_superuser:
        today = date.today()
        start_date = today - timedelta(days=7)
        count = (
            ApplyJobs.objects.filter(created_on__gte=start_date, created_on__lte=today, job__id=job_id)
            .annotate(day=Cast('created_on', DateField())).values("day")
            .annotate(application_count=Count('id')).order_by("day")
        )
        data_dict = {
            entry['day']: {
                'application_count': entry['application_count'],
                'date': entry['day'].day
            } for entry in count if entry['day'] is not None
        }
        result = {}
        current_date = start_date
        while current_date <= today:
            date_key = current_date.strftime('%d-%m-%y')
            if current_date in data_dict:
                result[date_key] = data_dict[current_date]
            else:
                result[date_key] = {
                    'application_count': 0,
                    'date': current_date.day
                }
            current_date += timedelta(days=1)
        return result
    return {"message" : "You are not authorized"}

#################################  J O B S  A P P L I C A T I O N S  #################################
@admin_api.get("/all_applications", response={200: List[ApplyCandidatesData], 409:Message}, description="Fetch all job applications")
@paginate
def all_applications(request):
    user = request.auth
    if user.is_superuser:
        applications = []
        for i in ApplyJobs.objects.all():
            candidates = []
            if not Personal.objects.filter(user=i.user).exists():
                continue
            personal = Personal.objects.get(user=i.user)
            employment = None
            if Employment.objects.filter(user=i.user).exists():
                employment = Employment.objects.filter(user=i.user).order_by('-id')
            qualification = None
            if Qualification.objects.filter(user=i.user).exists():
                qualification = Qualification.objects.filter(user=i.user).order_by('-id')
            applied_jobs = []
            for i in ApplyJobs.objects.filter(user=i.user):
                applied_jobs.append(i.job)
            applications.append({
                "id": i.id,
                'job': i.job,
                'applied_jobs': applied_jobs,
                "candidate": {"personal": {"personal": personal, "user": i.user}, "employment": employment, "qualification": qualification},
                "custom_qns": i.custom_qns,
                "status": i.status,
                "viewed": i.viewed,
                "created_on": i.created_on,
            })
        return applications
    return {"message" : "You are not authorized"}

#################################  C O M P A N Y  #################################
@admin_api.get("/all_company", response={200: List[AdminCompany], 409: Message}, description="All company datas")
@paginate
def all_company(request):
    companies = []
    for i in CompanyDetails.objects.all():
        jobs = JobPosts.objects.filter(company=i)
        companies.append({"name": i.name, "about": i.about, "website": i.website, "functional_area": i.functional_area, "address": i.address, "city": i.city, "country": i.country, "postal_code": i.postal_code, "contact_name": i.contact_name, "contact_land_number": i.contact_land_number, "contact_mobile_number": i.contact_mobile_number, "designation": i.designation, "logo": i.logo, "id": i.id, "jobs": jobs})
    return companies

#################################  S E E K E R S  #################################
@admin_api.get("/all_seekers", response={200: List[SeekerData], 409: Message}, description="All company datas")
@paginate
def all_seekers(request):
    seekers = []
    for profile in User.objects.filter(role="seeker"):
        if Personal.objects.filter(user=profile).exists():
            personal = Personal.objects.get(user=profile)
            employment = Employment.objects.filter(user=profile)
            qualification = Qualification.objects.filter(user=profile)
            seekers.append({"personal": {"personal": personal, "user": profile}, "employment": employment, "qualification": qualification})
    return seekers

#################################  S U B S C R I P T I O N S  #################################
@admin_api.get("/all_subs", response={200: List[AllSubsData], 405: Message, 409: Message}, description="All company datas")
@paginate
def all_subs(request, type: str = "all" ):
    if type not in ['seeker', 'recruiter', 'all']:
        return 405, {"message": "Type should be either seeker, recruiter or all"}
    subscriptions = Subscription.objects.filter(user__role=type) if type != "all" else Subscription.objects.all()
    all_sub = []
    for subs in subscriptions:
        seekers = []
        profile = subs.user
        if Personal.objects.filter(user=profile).exists():
            personal = Personal.objects.get(user=profile)
            employment = Employment.objects.filter(user=profile)
            qualification = Qualification.objects.filter(user=profile)
            seekers.append({"personal": {"personal": personal, "user": profile}, "employment": employment, "qualification": qualification})
        all_sub.append({
            "id": subs.id,
            "seeker": seekers,
            "plan": subs.plan,
            "remaining_posts": subs.remaining_posts,
            "transaction_id": subs.transaction_id,
            "subscribed_on": subs.subscribed_on.isoformat() if subs.subscribed_on else None
        })
    return all_sub

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
    return 409, {"message" : "You are not authorized to access plans"}

@admin_api.patch("/update_plans", response={201: Message, 409:Message}, description="Plan details")
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
    return 409, {"message" : "You are not authorized to access plans"}

@admin_api.delete("/delete_plans", response={201: Message, 404: Message, 409:Message}, description="Plan details")
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
async def banner_creation(request, data: BannerCreation, image: UploadedFile = File(...)):
    user = request.auth
    if user.is_superuser:
        banner = await Banner.objects.acreate(**data.dict())
        await sync_to_async(banner.image.save)(image.name, image)
        await banner.asave()
        return 201, {"message" : "Banner created successfuly"}
    return 409, {"message" : "You are not authorized to create banners"}

@admin_api.get("/banners", response={201: List[BannerData], 409:Message}, description="Banner details")
async def banners(request):
    user = request.auth
    if user.is_superuser:
        banner = [i async for i in Banner.objects.all()]
        return 201, banner
    return 409, {"message" : "You are not authorized to access banners"}

@admin_api.patch("/update_banner", response={201: Message, 409:Message}, description="Banner updations")
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

@admin_api.delete("/delete_banners", response={201: Message, 404: Message, 409:Message}, description="banner details")
async def delete_banners(request, id: int):
    user = request.auth
    if user.is_superuser:
        if await Banner.objects.filter(id=id).aexists():
            banner = await Banner.objects.aget(id=id)
            await banner.adelete()
            return 201, {"message" : "banner deleted successfuly"}
        return 404, {"message" : "banner doesnot exists"}
    return 409, {"message" : "You are not authorized to delete banners"}

#################################  N O T I F I C A T I O N S  #################################
@admin_api.post("/create_notification", response={201: Message, 404: Message, 409:Message}, description="Create Notifications")
def create_notification(request, data: NotificationCreation, image: UploadedFile = File(None)):
    notification = Notification.objects.create(title=data.title, description=data.description)
    if data.audience:
        for i in User.objects.filter(role=data.audience):
            notification.user.add(i.user.id)
    if image:
        notification.image = image
    if data.url:
        notification.url = data.url
    if data.user_id:
        for i in data.user_id:
            user = User.objects.get(id=i)
            notification.user.add(user)
    notification.save()
    return 201, {"message": "Notification created successfully"}

@admin_api.get("/all_notifications", response={200: List[AllNotifications], 404: Message, 409:Message}, description="All Notifications")
@paginate
def all_notifications(request):
    user = request.auth
    if user.is_superuser:
        notifications = []
        for i in Notification.objects.all().order_by('-id'):
            users = []
            for user in i.user.all():
                users.append(user.name)
            notifications.append({
                "id": i.id,
                "title": i.title,
                "description": i.description,
                "image": i.image,
                "url": i.url,
                "created_on": i.created_on.strftime("%d-%m-%Y %H:%M:%S"),
                "user": users,
                "read_by": i.read_by
            })
        return notifications
    return {"message" : "You are not authorized to access notifications"}

@admin_api.patch("/edit_notifications", response={200: Message, 409:Message}, description="Edit Notifications")
def edit_notifications(request, data: PatchDict[NotificationCreation]):
    user = request.auth
    if user.is_superuser:
        notification = Notification.objects.get(id=data.id)
        notification.title = data.title
        notification.description = data.description
        if data.image:
            notification.image = data.image
        if data.url:
            notification.url = data.url
        notification.save()
        return 200, {"message": "Notification updated successfully"}
    return 409, {"message" : "You are not authorized to access notifications"}

@admin_api.delete("/delete_notifications", response={200: Message, 404: Message, 409:Message}, description="Delete Notifications")
def delete_notifications(request, id: int):
    user = request.auth
    if user.is_superuser:
        notification = Notification.objects.get(id=id)
        notification.delete()
        return 200, {"message": "Notification deleted successfully"}
    return 409, {"message" : "You are not authorized to access notifications"}

#################################  A L L  U S E R S  #################################
@admin_api.get("/all_users", response={200: List[AllUsers], 409: Message}, description="All users (id, name, and phone number)")
async def all_users(request):
    user = request.auth
    if user.is_superuser:
        users = [i async for i in  User.objects.all().values('id', 'name', 'phone', 'role')]
        return 200, users
    return 409, {"message" : "You are not authorized to access users"}