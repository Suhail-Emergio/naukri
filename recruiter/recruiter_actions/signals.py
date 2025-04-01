from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from naukry.utils.email import send_interview_schedule
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from recruiter.recruiter_actions.models import EmailTemplate
from recruiter.company.models import CompanyDetails
from seeker.details.models import NotificationPreference

@receiver(post_save, sender=InterviewSchedule)
def log_model_save(sender, instance, created, **kwargs):
    action = None
    if created:
        action = "creation"
    elif kwargs.get('update_fields') and 'scheduled' in kwargs.get('update_fields'):
        action = "rescheduled"
    if action:
        if NotificationPreference.objects.get(user=instance.application.user).messages_recruiter == "immediately":
            company = CompanyDetails.objects.get(user=instance.user)
            subject =f"Your interview has been {"officially scheduled" if action == "creation" else "rescheduled"} for the position of {instance.application.job.title} on {instance.schedule}. This is an important step in the hiring process, offering an opportunity to showcase your skills, experience, and enthusiasm for the role. Please review the scheduled details carefully and make any necessary preparations to ensure a successful and productive conversation. We look forward to connecting with you and exploring how you can contribute to the success of our team!"
            if EmailTemplate.objects.filter(job=instance.application.job).exists():
                template = EmailTemplate.objects.get(job=instance.application.job)
                send_interview_schedule(instance.application.user.email, template.email, template.subject, template.body) if action == "creation" else send_interview_schedule(instance.application.user.email, template.email, subject="Interview rescheduled", body=subject)
            if instance.user.whatsapp_updations:
                send_updates(subject, instance.application.user.phone)
            if instance.user.onesignal_id and NotificationPreference.objects.get(user=instance.application.user).mobile_notifications:
                send_notifications(subject=subject, title=f"Interview {"Scheduled" if action == "creation" else "rescheduled"} - Next Steps Await!", onesignal_id=instance.user.onesignal_id)

@receiver(post_save, sender=InviteCandidate)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        if NotificationPreference.objects.get(user=instance.candidate.user).messages_recruiter == "immediately":
            subject = f"A company has invited your profile for a job post. Access you account for more information"
            title = "New Invitation"
            onesignal_id = instance.candidate.user.onesignal_id
            phone = instance.candidate.user.phone
            if instance.candidate.user.whatsapp_updations:
                send_updates(subject, phone)
            if onesignal_id and NotificationPreference.objects.get(user=instance.candidate.user).mobile_notifications:
                send_notifications(
                    subject=subject,
                    title=title,
                    onesignal_id=onesignal_id
                )