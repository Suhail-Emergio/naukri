from ninja import Router
from django.contrib.auth import get_user_model
from typing import *
from user.schema import *
from django.db.models import Q
from .schema import *
from .models import BlockedCompanies
from asgiref.sync import sync_to_async
from recruiter.recruiter_actions.models import InviteCandidate
from recruiter.company.models import CompanyDetails
from recruiter.company.schema import CompanyData
from recruiter.recruiter_actions.models import InterviewSchedule
from recruiter.recruiter_actions.schema import ScheduledInterviews

User = get_user_model()
seeker_actions_api = Router(tags=['seeker_actions'])

#################################  J O B  I N V I T A T I O N S  #################################
@seeker_actions_api.get("/job_invitations", response={200: List[JobInvitations], 409: Message}, description="Retrieve all invitations for a user") 
async def job_invitations(request):
    user = request.auth
    invites = [i async for i in InviteCandidate.objects.filter(candidate__user=user).order_by('-id')]
    return 200, invites

@seeker_actions_api.patch("/read_invitations", response={200: Message, 409: Message}, description="Mark an invitation as read") 
async def read_invitations(request, id:int):
    if await InviteCandidate.objects.filter(id=id).aexists():
        invite = await InviteCandidate.objects.aget(id=id)
        invite.read = True
        await invite.save()
        return 200, {"message": "Invitation read successfully"}
    return 404, {"message": "Invitation not found"}

@seeker_actions_api.delete("/reject_invitation", response={200: Message, 409: Message}, description="Reject an invitation") 
async def reject_invitation(request, id:int):
    if await InviteCandidate.objects.filter(id=id).aexists():
        invite = await InviteCandidate.objects.aget(id=id)
        invite.interested = False
        await invite.asave()
        return 200, {"message": "Invitation rejected successfully"}
    return 404, {"message": "Invitation not found"}

#################################  B L O C K /  U N B L O C K  C O M P A N I E S  #################################
@seeker_actions_api.post("/block_company", response={200: Message, 409: Message}, description="Block a company") 
async def block_company(request, id:int):
    user = request.auth
    if await CompanyDetails.objects.filter(id=id).aexists():
        if await BlockedCompanies.objects.filter(company__id=id, user=user).aexists():
            return 409, {"message": "Company already blocked"}
        await BlockedCompanies.objects.acreate(company__id=id, user=user)
        return 200, {"message": "Company blocked successfully"}
    return 404, {"message": "Company not found"}

@seeker_actions_api.get("/blocked_companies", response={200: List[CompanyData], 409: Message}, description="Retrieve all blocked companies") 
async def blocked_companies(request):
    user = request.auth
    blocked = [b async for b in BlockedCompanies.objects.filter(user=user)]
    return 200, blocked

@seeker_actions_api.post("/unblock_company", response={200: List[CompanyData], 409: Message}, description="Retrieve all blocked companies") 
async def unblock_company(request, id:int):
    user = request.auth
    if await BlockedCompanies.objects.filter(id=id).aexists():
        block = await BlockedCompanies.objects.aget(id=id)
        await block.adelete()
        return 200, {"message": "Company unblocked successfully"}
    return 404, {"message": "Blocked company not found"}

#################################  I N T E R V I E W S  #################################
@seeker_actions_api.get("/interviews_scheduled", response={200: List[ScheduledInterviews], 404: Message, 409: Message}, description="Invite candidates for job")
async def interviews_scheduled(request):
    user = request.auth
    interviews = [i async for i in InterviewSchedule.objects.filter(application__user=user).order_by('-id')]
    return 200, interviews