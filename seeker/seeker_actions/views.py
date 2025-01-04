from ninja import Router
from django.contrib.auth import get_user_model
from typing import *
from user.schema import *
from django.db.models import Q
from .schema import *
from asgiref.sync import sync_to_async
from recruiter.recruiter_actions.models import InviteCandidate

User = get_user_model()
seeker_actions_api = Router(tags=['seeker_actions'])

#################################  J O B  I N V I T A T I O N S  #################################
@seeker_actions_api.post("/job_invitations", response={200: List[JobInvitations], 409: Message}, description="Retrieve all invitations for a user") 
async def job_invitations(request):
    user = request.auth
    invites = [i async for i in InviteCandidate.objects.filter(candidate__user=user).order_by('-id')]
    return 200, invites

@seeker_actions_api.patch("/read_invitations", response={200: Message, 409: Message}, description="Retrieve all invitations for a user") 
async def read_invitations(request, id:int):
    if await InviteCandidate.objects.filter(id=id).aexists():
        invite = await InviteCandidate.objects.aget(id=id)
        invite.read = True
        await invite.save()
        return 200, {"message": "Invitation read successfully"}
    return 404, {"message": "Invitation not found"}

@seeker_actions_api.delete("/reject_invitation", response={200: Message, 409: Message}, description="Retrieve all invitations for a user") 
async def reject_invitation(request, id:int):
    if await InviteCandidate.objects.filter(id=id).aexists():
        invite = await InviteCandidate.objects.aget(id=id)
        invite.interested = False
        await invite.asave()
        return 200, {"message": "Invitation rejected successfully"}
    return 404, {"message": "Invitation not found"}