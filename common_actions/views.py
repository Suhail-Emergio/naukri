from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *
from administrator.admin_actions.models import Plans
from administrator.admin_actions.schema import PlanData

User = get_user_model()
common_api = Router(tags=['common'])

#################################  S U G G E S T I O N S  #################################
@common_api.post("/suggestion", response={201: Message, 409:Message}, description="Suggestion creations")
async def suggestions(request, data: SuggestionCreation):
    user = request.auth
    suggestion = await Suggestions.objects.acreate(**data.dict())
    await suggestion.asave()
    return 201, {"message" : "Suggestion created successfuly"}

#################################  P L A N S  #################################
@common_api.post("/all_plans", response={200: List[PlanData], 404: Message, 409:Message}, description="All plans")
async def all_plans(request):
    user = request.auth
    plans = [i async for i in Plans.objects.filter(audience=user.role)]
    return 200, plans

#################################  S U B S C R I P T I O N S  #################################
@common_api.post("/subscribe", response={201: Message, 404: Message, 409:Message}, description="Add subscription")
async def subscribe(request, data: SubscriptionCreation):
    user = request.auth
    if await Plans.objects.filter(id=data.plan_id).aexists():
        plan = await Plans.objects.aget(id=data.plan_id)
        audience = await sync_to_async(lambda: i.audience)()
        if user.role == audience:
            if await Subscription.objects.filter(user=user).aexists():
                already_sub = await Subscription.objects.aget(user=user)
                await already_sub.adelete()
            subscription = await Subscription.objects.acreate(user=user, plan=plan, transaction_id=data.transaction_id)
            await subscription.asave()
            user.subscribed = True
            await user.asave()
            return 201, {"message" : "Suggestion created successfuly"}
    return 404, {"message" : "Plan doesnot exists"}

@common_api.get("/subscriptions", response={200: SubscriptionData, 404: Message, 409:Message}, description="subscription taken by a user")
async def subscriptions(request):
    user = request.auth
    if await Subscription.objects.filter(user=user).aexists():
        subscription = await Subscription.objects.aget(user=user)
        return 200, subscription
    return 404, {"message" : "Subscription doesnot exists"}

@common_api.delete("/delete_subscription", response={200: Message, 404: Message, 409:Message}, description="subscription taken by a user")
async def delete_subscription(request, id: int):
    user = request.auth
    if await Subscription.objects.filter(id=id).aexists():
        subscription = await Subscription.objects.aget(id=id)
        await subscription.adelete()
        return 200, {"message" : "Subscription deleted successfully"}
    return 404, {"message" : "Subscription doesnot exists"}