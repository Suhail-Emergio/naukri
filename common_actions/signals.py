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
from naukry.utils.notification import send_notifications

@receiver([post_save], sender=Notification)
@receiver([post_save], sender=InviteCandidate)
def update_counts(sender, instance, **kwargs):
    if sender == InviteCandidate:
        users = [instance.candidate.user]
    else:  # Notification
        users = instance.user.all()
    if users:
        for i in users:
            if sender == Notification:
                description_words = instance.description.split()
                first_20_words = ' '.join(description_words[:20])
                send_notifications(
                    subject=first_20_words,
                    title=instance.title,
                    onesignal_id=i.onesignal_id
                )
            notification_count = Notification.objects.filter(user=i).exclude(read_by=i).count()
            if i.role == "seeker":
                invitation_count = InviteCandidate.objects.filter(candidate__user=i, read=False).count()
                message = {
                    "type": "counts_update",
                    "data": {
                        "notification_count": notification_count,
                        "invitation_count": invitation_count,
                    },
                }
                print(message, i.id)
                async_to_sync(manager.broadcast_to_user)(message=message, user_id=i.id)