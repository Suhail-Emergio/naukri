from django.db import models
from jobs.jobposts.models import JobPosts
from django.contrib.auth import get_user_model

User = get_user_model()

class SaveJobs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosts, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)

class ApplyJobs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosts, on_delete=models.CASCADE)
    custom_qns = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('applied', 'applied'), ('reviewing', 'reviewing'), ('interview_scheduled', 'interview_scheduled'), ('undecided', 'undecided'), ('shortlisted', 'shortlisted'), ('rejected', 'rejected')], default='applied')
    viewed = models.BooleanField(default=False)
    invited = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now=True)
    resume_downloaded = models.BooleanField(default=False)