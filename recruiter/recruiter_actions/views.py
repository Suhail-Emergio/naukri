from ninja import Router, Query, PatchDict, File, UploadedFile
from django.contrib.auth import get_user_model
from typing import *
from user.schema import *
from django.db.models import Q
from seeker.details.models import Preference, Personal, Employment
from .schema import *
from asgiref.sync import sync_to_async
from jobs.job_actions.models import ApplyJobs
from jobs.jobposts.models import JobPosts
from seeker.details.models import SearchApps
from seeker.details.schema import CountData
from common_actions.models import Subscription
from naukry.utils.profile_completion import completion_data
from django.utils import timezone
from .utils.csv_util import get_csv_data, create_csv
from .utils.candidate_gen import candidate_creation
from django.http import HttpResponse

User = get_user_model()
recruiter_actions_api = Router(tags=['recruiter_actions'])

#################################  A L L  S E E K E R  #################################
@recruiter_actions_api.get("/all_seekers", response={200: List[SeekerData], 404: Message, 409: Message}, description="Retrieve all candidates")
async def all_seekers(request):
    candidate = [i async for i in Personal.objects.exclude(user__is_active=False).order_by('-user__subscribed', '-id')]
    candidates = []
    for i in candidate:
        candidate_user = await sync_to_async(lambda: i.user)()
        print(timezone.now().date())
        if await SearchApps.objects.filter(user=candidate_user, date=timezone.now().date()).aexists():
            search_apps = await SearchApps.objects.aget(user=candidate_user, date=timezone.now().date())
            search_apps.count += 1
            await search_apps.asave()
        employment = None
        if await Employment.objects.filter(user=candidate_user).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate_user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate_user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate_user).order_by('-id')]
        candidates.append({"personal": {"personal": i, "user": candidate_user}, "employment": employment, "qualification": qualification})
    return 200, candidates

#################################  F I L T E R  C A N D I D A T E S  B A S E D  #################################
# @recruiter_actions_api.get("/resdex", response={200: List[SeekerData], 403: Message, 404: Message, 409: Message}, description="Retrieve all candidates based on filters")
# async def resdex(request,
#         job_id: int = None,
#         location: str = None,
#         keywords: List[str] = Query(None, description="List of keywords"), 
#         experience_year: int = None,
#         experience_month: int = None,
#         current_loc: str = None,
#         nationality: str = None,
#         salary_min: int = None,
#         salary_max: int = None,
#         gender: str = None,
#         additional: str = None,
#     ):
#     if await Subscription.objects.filter(user=request.auth, plan__resdex=True).aexists():
#         queries = Q()
#         candidates = []
#         if job_id:
#             if await JobPosts.objects.filter(id=job_id).aexists():
#                 job = await JobPosts.objects.aget(id=job_id)
#                 skills = await sync_to_async(lambda: job.skills)()
#                 keyword_query = Q()
#                 for keyword in skills:
#                     keyword_query |= Q(skills__contains=keyword.upper())
#                 queries &= keyword_query
#                 if location:
#                     queries &= Q(city__contains=location)
#                 users = []
#                 async for i in Personal.objects.filter(queries).order_by('-id'):
#                     users.append(await sync_to_async(lambda: i.user.id)())
#                 title = await sync_to_async(lambda: job.title)()
#                 q = Q()
#                 q &= Q(job_title__icontains=title)
#                 q &= Q(user__in=users)
#                 seen_users = set()
#                 async for i in Employment.objects.filter(q).order_by('-id'):
#                     user = await sync_to_async(lambda: i.user)()
#                     if user.id not in seen_users:
#                         seen_users.add(user.id)
#                         search_apps = await SearchApps.objects.filter(user=user).alatest('date')
#                         search_apps.count += 1
#                         await search_apps.asave()
#                         personal_ = await Personal.objects.aget(user=user)
#                         qualification = None
#                         if await Qualification.objects.filter(user=user).aexists():
#                             qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')]
#                         employment = None
#                         if await Employment.objects.filter(user=user).aexists():
#                             employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
#                         candidates.append({"personal": {"personal": personal_, "user": user}, "employment": employment, "qualification": qualification})
#         else:
#             if keywords:
#                 keyword_query = Q()
#                 for keyword in keywords:
#                     keyword_query |= Q(skills__contains=keyword)
#                 queries &= keyword_query
#             if experience_year or experience_month:
#                 if experience_year and experience_month:
#                     queries &= Q(total_experience_years__gte=experience_year) & Q(total_experience_months__gte=experience_month)
#                 else:
#                     queries &= Q(total_experience_years__gte=experience_year) | Q(total_experience_months__gte=experience_month)
#             if current_loc:
#                 queries &= Q(city__icontains=current_loc) | Q(state__icontains=current_loc)
#             if nationality:
#                 queries &= Q(nationality__icontains=nationality)
#             if salary_min and salary_max:
#                 queries &= Q(prefered_salary_pa__gte=salary_min) & Q(prefered_salary_pa__lte=salary_max)
#             if gender:
#                 queries &= Q(gender=gender) 
#             if queries:
#                 candidate = [i async for i in Personal.objects.filter(queries).exclude(user__is_active=False).order_by('-user__subscribed', '-id')]
#                 for i in candidate:
#                     user = await sync_to_async(lambda: i.user)()
#                     search_apps = await SearchApps.objects.filter(user=user).alatest('date')
#                     search_apps.count += 1
#                     await search_apps.asave()
#                     employment = None
#                     if await Employment.objects.filter(user=user).aexists():
#                         employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
#                     qualification = None
#                     if await Qualification.objects.filter(user=user).aexists():
#                         qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')]
#                     candidates.append({"personal": {"personal": i, "user": user}, "employment": employment, "qualification": qualification})
#         return 200, candidates
#     return 403, {"message": "Subscription not found"}

@recruiter_actions_api.get(
    "/resdex", 
    response={200: List[SeekerData], 403: Message, 404: Message, 409: Message}, 
    description="Retrieve all candidates based on filters"
)
async def resdex(
    request,
    job_id: int = None,
    location: str = None,
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
    user = request.user if hasattr(request, "user") else request.auth

    # Debug: check user
    print("Authenticated user:", user)

    # Check subscription
    has_access = await Subscription.objects.filter(
        user=user,
        plan__resdex=True
    ).aexists()

    if not has_access:
        return 403, {"message": "Subscription not found"}

    queries = Q()
    candidates = []

    if job_id:
        if await JobPosts.objects.filter(id=job_id).aexists():
            job = await JobPosts.objects.aget(id=job_id)
            skills = await sync_to_async(lambda: job.skills)()
            keyword_query = Q()
            for keyword in skills:
                keyword_query |= Q(skills__icontains=keyword.upper())
            queries &= keyword_query
            if location:
                queries &= Q(city__icontains=location)

            users = []
            async for i in Personal.objects.filter(queries).order_by('-id'):
                users.append(i.user.id)

            title = await sync_to_async(lambda: job.title)()
            q = Q(job_title__icontains=title, user__in=users)

            seen_users = set()
            async for i in Employment.objects.filter(q).order_by('-id'):
                user = i.user
                if user.id not in seen_users:
                    seen_users.add(user.id)
                    search_apps = await SearchApps.objects.filter(user=user).alatest('date')
                    search_apps.count += 1
                    await search_apps.asave()
                    personal_ = await Personal.objects.aget(user=user)
                    qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')] \
                        if await Qualification.objects.filter(user=user).aexists() else None
                    employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')] \
                        if await Employment.objects.filter(user=user).aexists() else None
                    candidates.append({
                        "personal": {"personal": personal_, "user": user},
                        "employment": employment,
                        "qualification": qualification
                    })
    else:
        if keywords:
            keyword_query = Q()
            for keyword in keywords:
                keyword_query |= Q(skills__icontains=keyword)
            queries &= keyword_query
        if experience_year or experience_month:
            if experience_year and experience_month:
                queries &= Q(total_experience_years__gte=experience_year) & Q(total_experience_months__gte=experience_month)
            else:
                queries &= Q(total_experience_years__gte=experience_year) | Q(total_experience_months__gte=experience_month)
        if current_loc:
            queries &= Q(city__icontains=current_loc) | Q(state__icontains=current_loc)
        if nationality:
            queries &= Q(nationality__icontains=nationality)
        if salary_min and salary_max:
            queries &= Q(prefered_salary_pa__gte=salary_min) & Q(prefered_salary_pa__lte=salary_max)
        if gender:
            queries &= Q(gender=gender)

        if queries:
            candidate = [i async for i in Personal.objects.filter(queries).exclude(user__is_active=False).order_by('-user__subscribed', '-id')]
            for i in candidate:
                user = i.user
                search_apps = await SearchApps.objects.filter(user=user).alatest('date')
                search_apps.count += 1
                await search_apps.asave()
                employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')] \
                    if await Employment.objects.filter(user=user).aexists() else None
                qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')] \
                    if await Qualification.objects.filter(user=user).aexists() else None
                candidates.append({
                    "personal": {"personal": i, "user": user},
                    "employment": employment,
                    "qualification": qualification
                })

    return 200, candidates


#################################  S A V E  C A N D I D A T E S  #################################
@recruiter_actions_api.post("/save_candidates", response={200: Message, 404: Message, 409: Message}, description="Retrieve all candidates based on filters")
async def save_candidate(request, id:int):
    if await Personal.objects.filter(id=id).aexists():
        personal = await Personal.objects.aget(id=id)
        user = request.auth
        if await SaveCandidate.objects.filter(user=user, candidate=personal).aexists():
            await SaveCandidate.objects.filter(user=user, candidate=personal).adelete()
            message = "Removed successfully"
        else:
            await SaveCandidate.objects.acreate(user=user, candidate=personal)
            message = "Saved successfully"
        return 200, {"message": message}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/saved_candidates", response={200: List[SavedCandidateSchema], 404: Message, 409: Message}, description="Retrieve all saved candidates")
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
        candidates.append({"id": i.id, "candidate": {"personal": {"personal": personal, "user": candidate_user}, "employment": employment, "qualification": qualification}, "created_on": i.created_on.strftime('%Y-%m-%d %H:%M:%S')})
    return 200, candidates

#################################  I N V I T E  C A N D I D A T E S  #################################
@recruiter_actions_api.post("/invite_candidates", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def invite_candidates(request, data: InviteCandidateSchema):
    user = request.auth
    if await Personal.objects.filter(id=data.candidate_id).aexists():
        if await JobPosts.objects.filter(id=data.job_id).aexists():
            personal = await Personal.objects.aget(id=data.candidate_id)
            job = await JobPosts.objects.aget(id=data.job_id)
            personal_user = await sync_to_async(lambda: personal.user)()
            candidate = await sync_to_async(lambda: personal.user)()
            if await InviteCandidate.objects.filter(user=user, candidate=personal, job=job).aexists():
                return 409, {"message": "Candidate already invited"}
            await InviteCandidate.objects.acreate(user=user, job=job, candidate=personal)
            return 200, {"message": "Candidate invited successfully"}
        return 404, {"message": "Job not found"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/candidates_invited", response={200: List[JobInvites], 404: Message, 409: Message}, description="Invite candidates for job")
async def candidates_invited(request, job_id: int = None):
    user = request.auth
    candidates = []
    invites = [i async for i in InviteCandidate.objects.filter(user=user, job__id=job_id).order_by('-id')] if job_id else [i async for i in InviteCandidate.objects.filter(user=user).order_by('-id')]
    for i in invites:
        personal = await sync_to_async(lambda: i.candidate)()
        job = await sync_to_async(lambda: i.job)()
        user = await sync_to_async(lambda: personal.user)()
        employment = None
        if await Employment.objects.filter(user=user).aexists():
            employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=personal.user).order_by('-id')]
        candidates.append({"id": i.id, "candidate":{"personal": {"personal": personal, "user": user}, "employment": employment, "qualification": qualification}, "read": i.read, "job": job, "created_on": i.created_on.strftime('%Y-%m-%d %H:%M:%S'), "status": i.status})
    return 200, candidates

@recruiter_actions_api.delete("/candidates_invited", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def delete_invitation(request, id: int):
    user = request.auth
    if await InviteCandidate.objects.filter(id=id).aexists():
        invites = await InviteCandidate.objects.aget(id=id)
        await invites.adelete()
        return 200, {"message": "Candidates invited deleted successfully"}
    return 404, {"message": "Candidate not found"}

#################################  I N T E R V I E W S  #################################
@recruiter_actions_api.get("/interviews_scheduled", response={200: List[ScheduledInterviews], 404: Message, 409: Message}, description="Invite candidates for job")
async def interviews_scheduled(request, job_id: int = None):
    user = request.auth
    interviews = [i async for i in InterviewSchedule.objects.filter(user=user, application__job__id=job_id).order_by('-id')] if job_id else [i async for i in InterviewSchedule.objects.filter(user=user).order_by('-id')]
    scheduled = []
    for i in interviews:
        candidate = await sync_to_async(lambda: i.application.user)()
        job = await sync_to_async(lambda: i.application.job)()
        personal = await Personal.objects.aget(user=candidate)
        employment = None
        if await Employment.objects.filter(user=candidate).aexists():
            employment = [i async for i in Employment.objects.filter(user=candidate).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=candidate).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=candidate).order_by('-id')]
        scheduled.append({"id": i.id, "candidate": {"personal": {"personal": personal, "user": candidate}, "employment": employment, "qualification": qualification}, "schedule": i.schedule, "job": job, "created_on": i.created_on.strftime('%Y-%m-%d %H:%M:%S %Z'), "interview_round": i.interview_round, "interview_status": i.interview_status})
    return 200, scheduled

@recruiter_actions_api.post("/schedule_interview", response={200: Message, 404: Message, 409: Message}, description="Invite candidates for job")
async def schedule_interview(request, data: InterviewScheduleSchema):
    user = request.auth
    if await Personal.objects.filter(id=data.candidate_id).aexists():
        if await JobPosts.objects.filter(id=data.job_id).aexists():
            personal = await Personal.objects.aget(id=data.candidate_id)
            candidate = await sync_to_async(lambda: personal.user)()
            job = await JobPosts.objects.aget(id=data.job_id)
            if await InterviewSchedule.objects.filter(user=user, application__user=candidate, application__job=job).aexists():
                return 409, {"message": "Interview already scheduled"}
            if await ApplyJobs.objects.filter(user=candidate, job=job).aexists():
                application = await ApplyJobs.objects.aget(user=candidate, job=job)
                await InterviewSchedule.objects.acreate(user=user, application=application, schedule=data.schedule)
                # application.status = "shortlisted"
                # await application.asave()
                return 200, {"message": "Interview scheduled successfully"}
            return 404, {"message": "Applied job not found"}
        return 404, {"message": "Job not found"}
    return 404, {"message": "Candidate not found"}

#################################  A P P L I C A T I O N S  #################################
@recruiter_actions_api.get("/export_application", response={200: None, 404: Message, 409: Message}, description="Reject application")
async def export_application(request, job_id: int = None):
    user = request.auth
    applications = []
    if job_id:
        job = [i async for i in JobPosts.objects.filter(id=job_id, company__user=user)]
    else:
        job = [i async for i in JobPosts.objects.filter(company__user=user)] ## All Jobs
    for i in job:
        job_apps = [i async for i in ApplyJobs.objects.filter(job=i).order_by('-id')]
        for i in job_apps:
            candidate = await sync_to_async(lambda: i.user)()
            job_title = await sync_to_async(lambda: i.job.title)()
            applications.append({"name": candidate.name, "email": candidate.email, "phone": candidate.phone, "job_title": job_title, "status": i.status, "applied_on": i.created_on.strftime('%Y-%m-%d %H:%M:%S')})
    if applications:
        # csv_data = await create_csv(applications)
        return await create_csv({"applications": applications})
    return 404, {"message": "No applications found"}

@recruiter_actions_api.patch("/reject_application", response={200: Message, 404: Message, 409: Message}, description="Reject application")
async def reject_application(request, id: int):
    user = request.auth
    if await ApplyJobs.objects.filter(id=id).aexists():
        application = await ApplyJobs.objects.aget(id=id)
        application.status = "rejected"
        await application.asave()
        return 200, {"message": "Application rejected successfully"}
    return 404, {"message": "Application not found"}

@recruiter_actions_api.patch("/update_interview", response={201: Message, 404: Message, 409: Message}, description="Interview update (Reschedule, Round update)")
async def update_interview(request, interview_id: int, data: PatchDict[UpdateInterviewRound]):
    user = request.auth
    if await InterviewSchedule.objects.filter(id=interview_id).aexists():
        interview = await InterviewSchedule.objects.aget(id=interview_id)
        if data.get("round") != interview.interview_round:
            interview.interview_status = "pending"
        for attr, value in data.items():
            setattr(interview, attr, value)
        await interview.asave()
        return 201, {"message": "Interview updated successfully"}
    return 404, {"message": "Interview not found"}

@recruiter_actions_api.patch("/update_application_status", response={200: Message, 404: Message, 409: Message}, description="Update application status")
async def update_application_status(request, id: int, data: UpdateApplicationStatus):
    user = request.auth
    if await ApplyJobs.objects.filter(id=id).aexists():
        application = await ApplyJobs.objects.aget(id=id)
        application.status = data.status
        await application.asave()
        return 200, {"message": "Application status updated successfully"}
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
async def template_updation(request, data: PatchDict[EmailTemplates], id: int):
    if await EmailTemplate.objects.filter(id=id).aexists():
        template = await EmailTemplate.objects.aget(id=id)
        if "job" in data:
            data["job"] = await JobPosts.objects.aget(id=data["job"])
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

#################################  C O U N T S  #################################
@recruiter_actions_api.get("/recruiter_counts", response={200: RecruiterCountsResponse, 404: Message}, description="Showing percentage of profile completion, counts, and remaining data to enter in profile")
async def recruiter_counts(request):
    if await Subscription.objects.filter(user=request.auth).aexists():
        profile_completion_percentage, empty_models, models_with_empty_fields = await completion_data(request.auth)
        interview_scheduled_count = await InterviewSchedule.objects.filter(user=request.auth).acount()
        application_count = await ApplyJobs.objects.filter(job__company__user=request.auth).acount()
        active_jobs_count = await JobPosts.objects.filter(company__user=request.auth, active=True).acount()
        inactive_jobs_count = await JobPosts.objects.filter(company__user=request.auth, active=False).acount()
        subscription = await Subscription.objects.aget(user=request.auth)
        plan = await sync_to_async(lambda: subscription.plan)()
        posts = await sync_to_async(lambda: plan.posts)()
        remaining_jobs_count = posts - await JobPosts.objects.filter(company__user=request.auth).acount()
        used_jobs_count = await JobPosts.objects.filter(company__user=request.auth).acount()
        return 200, {
            "profile_completion_percentage": profile_completion_percentage,
            "empty_models": empty_models,
            "models_with_empty_fields": models_with_empty_fields,
            "remaining_jobs_count": remaining_jobs_count,
            "used_jobs_count": used_jobs_count,
            "interview_scheduled_count": interview_scheduled_count,
            "application_count": application_count,
            "active_jobs_count": active_jobs_count,
            "inactive_jobs_count": inactive_jobs_count
        }
    return 404, {"message": "Subscription not found"}

#################################  R E S U M E S  D O W N L O A D E D  #################################
@recruiter_actions_api.get("/update_resume_count", description="update resume download value")
async def update_resume_count(request, application_id: int):
    if await ApplyJobs.objects.filter(id=application_id).aexists():
        job_applied = await ApplyJobs.objects.aget(id=application_id)
        job_applied.resume_downloaded = True
        await job_applied.asave()
        return 200, {"message": "Resume count updated successfully"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/resumes_downloaded", response={200: List[ResumeDownloadSchema], 404: Message, 409: Message}, description="fetch all resumes downloaded")
async def resumes_downloaded(request):
    user = request.auth
    downloaded = [i async for i in ApplyJobs.objects.filter(job__company__user=user, resume_downloaded=True).order_by('-id')]
    candidates = []
    for i in downloaded:
        candidate_user = await sync_to_async(lambda: i.user)()
        personal = await Personal.objects.aget(user=candidate_user)
        job = await sync_to_async(lambda: i.job)()
        candidates.append({"candidate": {"personal": personal, "user": candidate_user}, "job": job})
    return 200, candidates

#################################  V I E W E D  C A N D I D A T E S  #################################
@recruiter_actions_api.get("/create_view_candidates", response={200: Message, 404: Message, 409: Message}, description="update resume download value")
async def create_view_candidates(request, candidate_id: int):
    if await Personal.objects.filter(id=candidate_id).aexists():
        personal = await Personal.objects.aget(id=candidate_id)
        user = request.auth
        candidate = await sync_to_async(lambda: personal.user)()
        if await ViewedCandidate.objects.filter(user=user, candidate=personal).aexists():
            return 409, {"message": "Candidate already viewed"}
        await ViewedCandidate.objects.acreate(user=user, candidate=personal)
        return 200, {"message": "Candidate viewed successfully"}
    return 404, {"message": "Candidate not found"}

@recruiter_actions_api.get("/view_candidates", response={200: List[ViewedCandidateSchema], 404: Message, 409: Message}, description="update resume download value")
async def view_candidates(request):
    user = request.auth
    ## plan

    viewed = []
    async for i in ViewedCandidate.objects.filter(user=user).order_by('-id'):
        personal = await sync_to_async(lambda: i.candidate)()
        user = await sync_to_async(lambda: personal.user)()
        employment = None
        if await Employment.objects.filter(user=user).aexists():
            employment = [i async for i in Employment.objects.filter(user=user).order_by('-id')]
        qualification = None
        if await Qualification.objects.filter(user=user).aexists():
            qualification = [i async for i in Qualification.objects.filter(user=user).order_by('-id')]
        viewed.append({"candidate": {"personal": {"personal": personal, "user": user}, "employment": employment, "qualification": qualification}, "viewed_on": i.viewed_on.strftime('%Y-%m-%d %H:%M:%S %Z'), "id": i.id})
    return 200, viewed

#################################  V I E W E D  C A N D I D A T E S  #################################
@recruiter_actions_api.post("/add_candidates", response={200: Message, 404: Message, 405: Message, 409: Message}, description="Add candidates for job applications. If a CSV file is provided, it should contain a column named 'email' with candidate email addresses.")
async def add_candidates(request, job_id: int, csv: UploadedFile = File(None), data: Optional[AddCandidateSchema] = None):
    if job_id:
        if await JobPosts.objects.filter(id=job_id).aexists():
            job = await JobPosts.objects.aget(id=job_id)
            if data:
                if data.emails:
                    for email in data.emails:
                        await candidate_creation(email, job)
                    return 200, {"message": "Candidates added successfully"}
            else:
                status, message = await get_csv_data(csv, job)
                if not status:
                    return 405, message
                return 200, {"message": "Candidates added successfully"}
        return 404, {"message": "Job not found"}