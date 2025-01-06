from ninja import Router, Query, PatchDict
from django.contrib.auth import get_user_model
from typing import *
from user.schema import *
from django.db.models import Q
from seeker.details.models import Preference, Personal, Employment
from .schema import *
from asgiref.sync import sync_to_async
from jobs.job_actions.models import ApplyJobs
from jobs.jobposts.models import JobPosts

User = get_user_model()
recruiter_actions_api = Router(tags=['recruiter_actions'])

#################################  A L L  S E E K E R  #################################
@recruiter_actions_api.get("/all_seekers", response={200: List[SeekerData], 404: Message, 409: Message}, description="Retrieve all candidates")
async def all_seekers(request):
    candidate = [i async for i in Personal.objects.exclude(user__is_active=False).order_by('-id')]
    candidates = []
    for i in candidate:
        candidate_user = await sync_to_async(lambda: i.user)()
        employment = None
        if await Employment.objects.filter(user=candidate_user).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate_user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate_user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate_user).order_by('-id')]
        candidates.append({"personal": i, "employment": employment, "qualification": qualification})
    return 200, candidates

#################################  F I L T E R  C A N D I D A T E S  B A S E D  #################################
@recruiter_actions_api.get("/resdex", response={200: List[SeekerData], 404: Message, 409: Message}, description="Retrieve all candidates based on filters")
async def resdex(request,
        keywords: List[str] = Query(None, description="List of keywords"), 
        experience_year: int = None, 
        experience_month: int = None, 
        current_loc: str = None, 
        nationality: str = None, 
        salary_min: int = None, 
        salary_max: int = None,
        gender: str = None,
        additional: str = None,
    ):
    queries = Q()
    if keywords:
        queries &= Q(skills__in=keywords)
    if experience_year and experience_month:
        queries &= Q(total_experience_years__gte=experience_year) & Q(total_experience_month__gte=experience_month)
    if current_loc:
        queries &= Q(city__icontains=current_loc) | Q(state__icontains=current_loc)
    if nationality:
        queries &= Q(nationality__icontains=nationality)
    if salary_min and salary_max:
        queries &= Q(prefered_salary_pa__gte=salary_min) & Q(prefered_salary_pa__lte=salary_max)

    candidates = []
    if queries:
        candidate = [i async for i in Personal.objects.filter(queries).exclude(user__is_active=False).order_by('-id')]
        for i in candidate:
            user = await sync_to_async(lambda: i.user)()
            employment = None
            if await Employment.objects.filter(user=user).aexists():
                employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
            qualification = None
            if await Qualification.objects.filter(user=user).aexists():
                qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')]
            candidates.append({"personal": i, "employment": employment, "qualification": qualification})
    return 200, candidates

#################################  S A V E  C A N D I D A T E S  #################################
@recruiter_actions_api.post("/save_candidates", response={200: Message, 404: Message, 409: Message}, description="Retrieve all candidates based on filters")
async def save_candidate(request, id:int):
    if await Personal.objects.filter(id=id).aexists():
        personal = await Personal.objects.aget(id=id)
        user = request.auth
        if await SaveCandidate.objects.filter(user=user, candidate=personal).aexists():
            return 409, {"message": "Candidate already saved"}
        await SaveCandidate.objects.acreate(user=user, candidate=personal)
        return 200, {"message": "Candidate saved successfully"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/saved_candidates", response={200: List[SeekerData], 404: Message, 409: Message}, description="Retrieve all saved candidates")
async def saved_candidates(request):
    user = request.auth
    saved = [i async for i in SaveCandidate.objects.filter(user=user).order_by('-id')]
    candidates = []
    for i in saved:
        personal = await sync_to_async(lambda: i.candidate)()
        candidate_user = await sync_to_async(lambda: personal.user)()
        employment = None
        if await Employment.objects.filter(user=candidate_user).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate_user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate_user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate_user).order_by('-id')]
        candidates.append({"personal": personal, "employment": employment, "qualification": qualification})
    return 200, candidates

#################################  I N V I T E  C A N D I D A T E S  #################################
@recruiter_actions_api.post("/invite_candidates", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def invite_candidates(request, data: InviteCandidateSchema):
    user = request.auth
    if await Personal.objects.filter(id=data.candidate_id).aexists():
        if await JobPosts.objects.filter(id=data.job_id).aexists():
            personal = await Personal.objects.aget(id=data.candidate_id)
            job = await JobPosts.objects.aget(id=data.job_id)
            candidate = await sync_to_async(lambda: personal.user)()
            if await InviteCandidate.objects.filter(user=user, application__user=candidate, application__job=job).aexists():
                return 409, {"message": "Candidate already invited"}
            await InviteCandidate.objects.acreate(user=user, application__user=candidate, application__job=job)
            return 200, {"message": "Candidate invited successfully"}
        return 404, {"message": "Job not found"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/candidates_invited", response={200: List[JobInvitations], 404: Message, 409: Message}, description="Invite candidates for job")
async def candidates_invited(request, job_id: int = None):
    user = request.auth
    candidates = []
    invites = [i async for i in InviteCandidate.objects.filter(user=user, application__job__id=job_id).order_by('-id')] if job_id else [i async for i in InviteCandidate.objects.filter(user=user).order_by('-id')]
    for i in invites:
        personal = await sync_to_async(lambda: i.candidate)()
        user = await sync_to_async(lambda: personal.user)()
        employment = None
        if await Employment.objects.filter(user=user).aexists():
            employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=personal.user).order_by('-id')]
        candidates.append({"candidate":{"personal": personal, "employment": employment, "qualification": qualification}, "read": i.read})
    return 200, candidates

@recruiter_actions_api.delete("/candidates_invited", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def delete_invitation(request, id: int):
    user = request.auth
    if await InviteCandidate.objects.filter(id=id).aexists():
        invites = await InviteCandidate.objects.aget(id=id)
        await invites.adelete()
        return 200, {"message": "Candidates invited deleted successfully"}
    return 404, {"message": "Job not found"}

#################################  I N T E R V I E W S  #################################
@recruiter_actions_api.get("/interviews_scheduled", response={200: List[ScheduledInterviews], 404: Message, 409: Message}, description="Invite candidates for job")
async def interviews_scheduled(request, job_id: int = None):
    user = request.auth
    interviews = [i async for i in InterviewSchedule.objects.filter(user=user, job__id=job_id).order_by('-id')] if job_id else [i async for i in InterviewSchedule.objects.filter(user=user).order_by('-id')]
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
        scheduled.append({"candidate": {"personal": personal, "employment": employment, "qualification": qualification}, "schedule": i.schedule, "created_on": i.created_on})
    return 200, interviews

@recruiter_actions_api.post("/schedule_interview", response={200: List[ScheduledInterviews], 404: Message, 409: Message}, description="Invite candidates for job")
async def schedule_interview(request, data: InterviewScheduleSchema):
    user = request.auth
    if await Personal.objects.filter(id=data.candidate_id).aexists():
        if await JobPosts.objects.filter(id=data.job_id).aexists():
            personal = await Personal.objects.aget(id=data.candidate_id)
            candidate = await sync_to_async(lambda: personal.user)()
            job = await JobPosts.objects.aget(id=data.job_id)
            if await InterviewSchedule.objects.filter(user=user, application__user=candidate, application__job=job).aexists():
                return 409, {"message": "Interview already scheduled"}
            application = await ApplyJobs.objects.aget(user=candidate, job=job)
            await InterviewSchedule.objects.acreate(user=user, application=application, schedule=data.schedule)
            return 200, {"message": "Interview scheduled successfully"}
        return 404, {"message": "Job not found"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.delete("/reject_application", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def reject_application(request, id: int):
    user = request.auth
    if await ApplyJobs.objects.filter(id=id).aexists():
        application = await ApplyJobs.objects.aget(id=id)
        application.status = "rejected"
        await application.asave()
        return 200, {"message": "Application rejected successfully"}
    return 404, {"message": "Application not found"}

#################################  E M A I L S  #################################
@recruiter_actions_api.get("/email_templates", response={200: List[EmailTemplates], 404: Message, 409: Message}, description="Retrieve all email templates created by user")
async def templates(request):
    user = request.auth
    templates = [i async for i in EmailTemplate.objects.filter(user=user).order_by('-id')]
    return 200, templates

@recruiter_actions_api.post("/create_template", response={200: Message, 404: Message, 409: Message}, description="Create email templates")
async def template_creation(request, data: TemplateCreation):
    user = request.auth
    if await JobPosts.objects.filter(id=data.job_id).aexists():
        job = await JobPosts.objects.aget(id=data.job_id)
        if await EmailTemplate.objects.filter(user=user, job=job).aexists():
            return 409, {"message": "Template already created for this job"}
        await EmailTemplate.objects.acreate(user=user, job=job, **data.dict())
        return 200, {"message": "Template created successfully"}
    return 404, {"message": "Job not found"}

@recruiter_actions_api.patch("/update_template", response={200: Message, 404: Message, 409: Message}, description="Update email template")
async def template_updation(request, data: PatchDict[TemplateCreation], id: int):
    if await EmailTemplate.objects.filter(id=id).aexists():
        template = await EmailTemplate.objects.aget(id=id)
        for attr, value in data.items():
            setattr(template, attr, value)
        await template.asave()
        return 200, {"message": "Template updated successfully"}
    return 404, {"message": "Template not found"}

@recruiter_actions_api.delete("/delete_template", response={200: Message, 404: Message, 409: Message}, description="Delete email template")
async def template_deletion(request, id: int):
    if await EmailTemplate.objects.filter(id=id).aexists():
        template = await EmailTemplate.objects.aget(id=id)
        await template.adelete()
        return 200, {"message": "Template deleted successfully"}
    return 404, {"message": "Template not found"}