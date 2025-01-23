from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from common_actions.models import Notification
from recruiter.recruiter_actions.models import InviteCandidate
import httpx
from django.conf import settings
from asgiref.sync import async_to_sync
from web_sockets.main import manager
from jobs.job_actions.models import ApplyJobs

@receiver([post_save], sender=Notification)
@receiver([post_save], sender=InviteCandidate)
# @receiver([post_save], sender=ApplyJobs)
def update_counts(sender, instance, **kwargs):
    user = instance.candidate.user
    notification_count = Notification.objects.filter(user=user, read_by=False).count()
    if user.role == "seeker":
        invitation_count = InviteCandidate.objects.filter(candidate__user=user, read=False).count()
        message = {
            "type": "counts_update",
            "data": {
                "notification_count": notification_count,
                "invitation_count": invitation_count,
            },
        }
        print(message, user.id)
        async_to_sync(manager.broadcast_to_user)(message=message, user_id=user.id)