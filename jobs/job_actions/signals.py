from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from naukry.utils.email import send_interview_schedule
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications

@receiver(post_save, sender=ApplyJobs)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        subject = f"A new application for Job: {instance.job.title}"
        title = "New Application"
        onesignal_id = instance.job.company.user.onesignal_id
        phone = instance.job.company.user.phone
    else:
        if hasattr(instance, '_loaded_values'):
            old_status = instance._loaded_values.get('status')
            new_status = instance.status
            if old_status != new_status:
                subject=f"Updation on Your Application for the Job: {instance.job.title}"
                title = "Your Application Status Has Changed"
                onesignal_id = instance.user.onesignal_id
                phone = instance.user.phone
    if onesignal_id:
        send_notifications(
            subject=subject,
            title=title,
            onesignal_id=onesignal_id
        )
    send_updates(subject, phone)
    return