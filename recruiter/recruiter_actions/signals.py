from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from naukry.utils.email import send_interview_schedule
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from recruiter.recruiter_actions.models import EmailTemplate
from recruiter.company.models import CompanyDetails

@receiver(post_save, sender=InterviewSchedule)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        company = CompanyDetails.objects.get(user=instance.user)
        if EmailTemplate.objects.filter(job=instance.application.job).exists():
            template = EmailTemplate.objects.get(job=instance.application.job)
            send_interview_schedule(instance.candidate.user.email, template.email, template.subject, template.body)
        body=(
            f"Hello! This is a message from {company.name}.\n"
            f"interview for the position of {job_title} has been scheduled at {instance.schedule}.\n"
            f"Please check your email for further details and instructions. We look forward to connecting with you!"
        ),
        send_updates(body, instance.candidate.user.phone)
        if instance.user.onesignal_id:
            send_notifications(subject=f"Interview is Scheduled for the Position: {instance.application.job.title}", title="Interview Scheduled - Next Steps Await!", onesignal_id=instance.user.onesignal_id)
            send_updates(f"Interview is Scheduled for the Position: {instance.application.job.title}", instance.user.phone)

@receiver(post_save, sender=InviteCandidate)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        subject = f"A company has invited your profile for a job post. Access you acount for more information"
        title = "New Invitation"
        onesignal_id = instance.candidate.user.onesignal_id
        phone = instance.candidate.user.phone
        if onesignal_id:
            send_notifications(
                subject=subject,
                title=title,
                onesignal_id=onesignal_id
            )
        send_updates(subject, phone)
    return