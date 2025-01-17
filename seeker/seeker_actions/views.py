from ninja import Router
from django.contrib.auth import get_user_model
from typing import *
from user.schema import *
from django.db.models import Q
from .schema import *
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import ExtractMonth, TruncDate, ExtractDay
from django.db.models import Case, When, IntegerField, F, Sum
from .models import BlockedCompanies
from asgiref.sync import sync_to_async
from recruiter.recruiter_actions.models import InviteCandidate, SaveCandidate
from recruiter.company.models import CompanyDetails
from recruiter.company.schema import CompanyData
from recruiter.recruiter_actions.models import InterviewSchedule
from recruiter.recruiter_actions.schema import ScheduledInterviews
from seeker.details.models import SearchApps
from jobs.jobposts.schema import JobData
from seeker.details.models import *

User = get_user_model()
seeker_actions_api = Router(tags=['seeker_actions'])

#################################  J O B  I N V I T A T I O N S  #################################
@seeker_actions_api.get("/job_invitations", response={200: List[JobInvitations], 409: Message}, description="Retrieve all invitations for a user") 
async def job_invitations(request):
    user = request.auth
    jobs = []
    async for i in InviteCandidate.objects.filter(candidate__user=user).order_by('-id'):
        job = await sync_to_async(lambda: i.job)()
        jobs.append({
            "job": job,
            "read": await sync_to_async(lambda: i.read)(),
            "interested": await sync_to_async(lambda: i.interested)(),
            "created_on": await sync_to_async(lambda: i.created_on)(),
        })
    return 200, jobs

@seeker_actions_api.patch("/read_invitations", response={200: Message, 404: Message, 409: Message}, description="Mark an invitation as read") 
async def read_invitations(request, id:int):
    if await InviteCandidate.objects.filter(job__id=id).aexists():
        invite = await InviteCandidate.objects.aget(job__id=id)
        invite.read = True
        await invite.asave()
        return 200, {"message": "Invitation read successfully"}
    return 404, {"message": "Invitation not found"}

@seeker_actions_api.delete("/reject_invitation", response={200: Message, 404: Message, 409: Message}, description="Reject an invitation") 
async def reject_invitation(request, id:int):
    if await InviteCandidate.objects.filter(job__id=id).aexists():
        invite = await InviteCandidate.objects.aget(job__id=id)
        invite.interested = False
        await invite.asave()
        return 200, {"message": "Invitation rejected successfully"}
    return 404, {"message": "Invitation not found"}

#################################  B L O C K /  U N B L O C K  C O M P A N I E S  #################################
@seeker_actions_api.post("/block_company", response={200: Message, 409: Message}, description="Block a company") 
async def block_company(request, id:int):
    user = request.auth
    if await CompanyDetails.objects.filter(id=id).aexists():
        company = await CompanyDetails.objects.aget(id=id)
        if await BlockedCompanies.objects.filter(company=company, user=user).aexists():
            return 409, {"message": "Company already blocked"}
        await BlockedCompanies.objects.acreate(company=company, user=user)
        return 200, {"message": "Company blocked successfully"}
    return 404, {"message": "Company not found"}

@seeker_actions_api.get("/blocked_companies", response={200: List[BlockedComp], 409: Message}, description="Retrieve all blocked companies") 
async def blocked_companies(request):
    user = request.auth
    blocked = []
    async for i in BlockedCompanies.objects.filter(user=user):
        company = await sync_to_async(lambda: i.company)()
        blocked_on = await sync_to_async(lambda: i.blocked_on)()
        blocked.append({
            "company": company,
            "blocked_on": blocked_on
        })
    return 200, blocked

@seeker_actions_api.post("/unblock_company", response={200: Message, 404: Message, 409: Message}, description="Retrieve all blocked companies") 
async def unblock_company(request, id:int):
    user = request.auth
    if await BlockedCompanies.objects.filter(company__id=id).aexists():
        block = await BlockedCompanies.objects.aget(company__id=id)
        await block.adelete()
        return 200, {"message": "Company unblocked successfully"}
    return 404, {"message": "Blocked company not found"}

#################################  I N T E R V I E W S  #################################
@seeker_actions_api.get("/interviews_scheduled", response={200: List[ScheduledInterviews], 404: Message, 409: Message}, description="Invite candidates for job")
async def interviews_scheduled(request):
    user = request.auth
    interviews = [i async for i in InterviewSchedule.objects.filter(application__user=user).order_by('-id')]
    scheduled = []
    for i in interviews:
        candidate = await sync_to_async(lambda: i.application.user)()
        personal = await Personal.objects.aget(user=candidate)
        employment = None
        if await Employment.objects.filter(user=candidate).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate).order_by('-id')]
        scheduled.append({"candidate": {"personal": {"personal": personal, "user": candidate}, "employment": employment, "qualification": qualification}, "schedule": i.schedule, "created_on": i.created_on})
    return 200, scheduled

#################################  R E C R U I T E R  A C T I O N S  #################################
@seeker_actions_api.get("/recruiter_action", description="Count, & Info on recruiter actions")
def recruiter_action(request):
    user = request.auth
    today = timezone.now()
    ninety_days_ago = today - timedelta(days=90)

    ## Count, & Info for bookmarking user profile by recruiter
    saved_candidates = []
    for i in SaveCandidate.objects.filter(created_on__gte=ninety_days_ago, candidate__user=user):
        saved_candidates.append({"company": CompanyDetails.objects.get(user=i.user).name, "created_on": i.created_on.isoformat()})

    ## Count, & Info for nvites send to user by recruiter
    invited_data = []
    for i in InviteCandidate.objects.filter(created_on__gte=ninety_days_ago, candidate__user=user):
        invited_data.append({"company": i.job.company.name, "job": i.job.title, "created_on": i.created_on.isoformat()})

    count_invited = InviteCandidate.objects.filter(created_on__gte=ninety_days_ago, candidate__user=user).count()
    count_saved = SaveCandidate.objects.filter(created_on__gte=ninety_days_ago, candidate__user=user).count()
    recruiter_actions = [{
        "saved": saved_candidates,
        "invitations": invited_data,
        "count_total": count_invited + count_saved,
        "count_invited": count_invited,
        "count_saved": count_saved,
    }]
    return recruiter_actions

@seeker_actions_api.get("/seach_apps", description="Search appearences of a seeker")
def seach_apps(request, type: str = ""):
    user = request.auth
    today = timezone.now()
    appearences = []
    appearences = 0
    if type == "week":
        start_date = today - timedelta(days=7) 
        appearences = (
            SearchApps.objects.filter(user=user, date__range=[start_date, today])
            .annotate(truncated_date=TruncDate("date"))
            .values("date", "truncated_date")
            .annotate(total_count=Sum("count"))
            .order_by("truncated_date")
        )
    elif type == "month":
        start_date = today - timedelta(days=30)
        appearences = (SearchApps.objects.filter(user=user, date__range=[start_date, today]).annotate(day_of_month=ExtractDay('date'), date_range=Case(When(day_of_month__lte=10, then=1), When(day_of_month__lte=20, then=2), When(day_of_month__lte=31, then=3), output_field=IntegerField(),)).values('date_range').annotate(total_count=Sum('count')).order_by('date_range'))
    else:
        start_date = today - timedelta(days=90)
        appearences = (SearchApps.objects.filter(user=user, date__range=[start_date, today]).annotate(month=ExtractMonth("date")).values("month").annotate(total_count=Sum("count")).values("month", "total_count").order_by('date'))
    return list(appearences)