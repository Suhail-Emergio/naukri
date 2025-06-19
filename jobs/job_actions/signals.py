from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from naukry.utils.email import send_interview_schedule
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from seeker.details.models import NotificationPreference
from common_actions.models import Notification
from web_sockets.main import manager
from asgiref.sync import async_to_sync

@receiver(post_save, sender=ApplyJobs)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        subject = f"A new application for Job: {instance.job.title}"
        title = "New Application"
        onesignal_id = instance.job.company.user.onesignal_id
        phone = instance.job.company.user.phone
        if NotificationPreference.objects.get(user=instance.job.company.user).applications != "ban":
            if onesignal_id  and NotificationPreference.objects.get(user=instance.job.company.user).mobile_notifications:
                send_notifications(
                    subject=subject,
                    title=title,
                    onesignal_id=onesignal_id
                )
            send_updates(subject, phone)
    else:
        if hasattr(instance, '_loaded_values'):
            old_status = instance._loaded_values.get('status')
            new_status = instance.status
            if old_status != new_status:
                subject=f"Updation on Your Application for the Job: {instance.job.title}"
                title = "Your Application Status Has Changed"
                onesignal_id = instance.user.onesignal_id
                phone = instance.user.phone
                if NotificationPreference.objects.get(user=instance.user).applications != "ban":
                    if onesignal_id  and NotificationPreference.objects.get(user=instance.job.company.user).mobile_notifications:
                        send_notifications(
                            subject=subject,
                            title=title,
                            onesignal_id=onesignal_id
                        )
                    send_updates(subject, phone)

    user = instance.job.company.user
    notification_count = Notification.objects.filter(user=user, read_by=False).count()
    if user.role == "recruiter":
        application_count = ApplyJobs.objects.filter(job__company__user=user, viewed=False).count()
        message = {
            "type": "counts_update",
            "data": {
                "notification_count": notification_count,
                "application_count": application_count,
            },
        }
        print(message, user.id)
        async_to_sync(manager.broadcast_to_user)(message=message, user_id=user.id)
    return