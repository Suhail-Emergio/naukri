from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from naukry.utils.email import send_interview_schedule
from naukry.utils.twilio import send_updates
from recruiter.recruiter_actions.models import EmailTemplate
from recruiter.company.models import CompanyDetails

@receiver(post_save, sender=InterviewSchedule)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        company = CompanyDetails.objects.get(user=instance.user)
        send_updates(company.name, instance.job.title, instance.schedule, instance.candidate.user.phone)
        if EmailTemplate.objects.filter(job=instance.job).exists():
            template = EmailTemplate.objects.get(job=instance.job)
            send_interview_schedule(instance.candidate.user.email, template.subject, template.body)