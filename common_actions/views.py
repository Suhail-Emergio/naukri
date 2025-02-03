import asyncio
from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *
from administrator.admin_actions.models import Plans, Banner
from administrator.admin_actions.schema import PlanData, BannerData

User = get_user_model()
common_api = Router(tags=['common'])

#################################  S U G G E S T I O N S  #################################
@common_api.post("/suggestion", response={201: Message, 409:Message}, description="Suggestion creations")
async def suggestions(request, data: SuggestionCreation):
    user = request.auth
    suggestion = await Suggestions.objects.acreate(**data.dict(), user=user)
    await suggestion.asave()
    return 201, {"message" : "Suggestion created successfuly"}

#################################  P L A N S  #################################
@common_api.get("/all_plans", response={200: List[PlanData], 404: Message, 409:Message}, description="All plans")
async def all_plans(request):
    user = request.auth
    plans = [i async for i in Plans.objects.filter(audience=user.role)]
    return 200, plans

#################################  B A N N E R S  #################################
@common_api.get("/banners", response={200: List[BannerData], 404: Message, 409:Message}, description="All plans")
async def banners(request):
    user = request.auth
    banner = [i async for i in Banner.objects.all()]
    return 200, banner

#################################  S U B S C R I P T I O N S  #################################
@common_api.post("/subscribe", auth=None, response={201: Message, 404: Message, 409:Message}, description="Add subscription")
async def subscribe(request, data: SubscriptionCreation):
    if await User.objects.filter(username=data.phone).aexists():
        user = await User.objects.aget(username=data.phone)
        role = await sync_to_async(lambda: user.role)()
        if await Plans.objects.filter(id=data.plan_id).aexists():
            plan = await Plans.objects.aget(id=data.plan_id)
            audience = await sync_to_async(lambda: plan.audience)()
            if role == audience:
                if await Subscription.objects.filter(user=user).aexists():
                    already_sub = await Subscription.objects.aget(user=user)
                    await already_sub.adelete()
                subscription = await Subscription.objects.acreate(user=user, plan=plan, transaction_id=data.transaction_id)
                await subscription.asave()
                user.subscribed = True
                await user.asave()
                return 201, {"message" : "Subscription created successfuly"}
        return 404, {"message" : "Plan doesnot exists"}
    return 409, {"message" : "User doesnot exists"}

@common_api.get("/subscriptions", response={200: SubscriptionData, 404: Message, 409:Message}, description="subscription taken by a user")
async def subscriptions(request):
    user = request.auth
    if await Subscription.objects.filter(user=user).aexists():
        subscription = await Subscription.objects.aget(user=user)
        return 200, {
            "id": await sync_to_async(lambda: subscription.id)(),
            "plan": await sync_to_async(lambda: subscription.plan)(),
            "remaining_posts": await sync_to_async(lambda: subscription.remaining_posts)(),
            "transaction_id": await sync_to_async(lambda: subscription.transaction_id)(),
            "subscribed_on": await sync_to_async(lambda: subscription.subscribed_on)(),
        }
    return 404, {"message" : "Subscription doesnot exists"}

@common_api.delete("/delete_subscription", response={200: Message, 404: Message, 409:Message}, description="delete subscription taken by a user")
async def delete_subscription(request):
    user = request.auth
    if await Subscription.objects.filter(user=user).aexists():
        subscription = await Subscription.objects.aget(user=user)
        await subscription.adelete()
        return 200, {"message" : "Subscription deleted successfully"}
    return 404, {"message" : "Subscription doesnot exists"}

#################################  S U B S C R I P T I O N S  #################################
@common_api.get("/notification", response={200: List[NotificationData], 404: Message, 409:Message}, description="Notification based on logged user")
def notifications(request):
    user = request.auth
    notification = []

    # @sync_to_async
    # def fetch_notifications(user):
    #     return user.notifications.all().order_by('-id')

    # noti = await fetch_notifications(user)
    for i in user.notifications.all().order_by('-id'):
        read = i.read_by.filter(id=user.id).exists()
        notification.append({'id': i.id, 'noti': i, 'read': read})
    # asyncio.create_task(mark_notifications_read(user.notifications.all().order_by('-id'), user))
    return 200, notification

@common_api.get("/read_notification", response={200: Message, 409:Message}, description="Notification based on logged user")
def read_notifications(request):
    user = request.auth
    for i in user.notifications.all().order_by('-id'):
        notification.read_by.add(user)
        notification.save()
    return 200, {"message": "Notifications marked as read"}

@common_api.delete("/delete_notification", response={200: Message, 404: Message, 409:Message}, description="Delete notfications")
async def delete_notification(request, id: int):
    if await Notification.objects.filter(id=id).aexists():
        noti = await Notification.objects.aget(id=id)
        await noti.user.aremove(request.auth)
        return 200, {"messsage": "Notitfication data deleted successfully"}
    return 404, {"messsage": "Notitfication data not found"}