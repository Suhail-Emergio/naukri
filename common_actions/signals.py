from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from common_actions.models import Notification
from recruiter.recruiter_actions.models import InviteCandidate
import httpx
from django.conf import settings
import asyncio

@receiver([post_save, post_delete], sender=Notification)
@receiver([post_save, post_delete], sender=InviteCandidate)
def update_counts(sender, instance, **kwargs):
    async def async_update():
        user = instance.user
        notification_count = await Notification.objects.filter(user=user, read=False).acount()
        invitation_count = await InviteCandidate.objects.filter(user=user, status='pending').acount()
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{settings.WEBSOCKET_URL}/update_counts",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "notification_count": notification_count,
                    "invitation_count": invitation_count
                }
            )
        asyncio.run(async_update())