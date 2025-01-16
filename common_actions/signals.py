from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from common_actions.models import Notification
from recruiter.recruiter_actions.models import InviteCandidate
import httpx
from django.conf import settings
import asyncio
from ninja_jwt.tokens import RefreshToken, AccessToken
from web_sockets.main import ConnectionManager as manager
import json

@receiver([post_save], sender=Notification)
@receiver([post_save], sender=InviteCandidate)
def update_counts(sender, instance, **kwargs):
    user = instance.user
    async def async_update():
        print("WORKING!.....")
        token = AccessToken.for_user(user)
        notification_count = await Notification.objects.filter(user=user, read_by=False).acount()
        invitation_count = await InviteCandidate.objects.filter(user=user, read=False).acount()
        message = {
            "type": "counts_update",
            "data": {
                "notification_count": notification_count,
                "invitation_count": invitation_count,
            },
        }
        await manager.broadcast_to_user(json.dumps(message), user.id)
    asyncio.run(async_update())