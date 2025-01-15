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

@receiver([post_save, post_delete], sender=Notification)
@receiver([post_save, post_delete], sender=InviteCandidate)
def update_counts(sender, instance, **kwargs):
    async def async_update():
        user = instance.user
        token = AccessToken.for_user(user)
        notification_count = await Notification.objects.filter(user=user, read=False).acount()
        invitation_count = await InviteCandidate.objects.filter(user=user, status='pending').acount()
        message = {
            "type": "counts_update",
            "data": {
                "notification_count": notification_count,
                "invitation_count": invitation_count,
            },
        }
        await manager.broadcast_to_user(json.dumps(message), user.id)
    asyncio.run(async_update())