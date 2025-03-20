from django.db import models
from django.contrib.auth import get_user_model
from seeker.details.models import Personal
from jobs.jobposts.models import JobPosts
from jobs.job_actions.models import ApplyJobs

User = get_user_model()

class SaveCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)

class ViewedCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE)
    viewed_on = models.DateTimeField(auto_now=True)

class InviteCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(JobPosts, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=[('applied', 'applied'), ('reviewing', 'reviewing'), ('pending', 'pending'), ('rejected', 'rejected')], default='pending')
    created_on = models.DateTimeField(auto_now=True)

class EmailTemplate(models.Model):
    name = models.CharField(max_length=30, default="")
    email = models.CharField(max_length=100, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosts, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

class InterviewSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(ApplyJobs, on_delete=models.CASCADE)
    schedule = models.DateTimeField()
    created_on = models.DateTimeField(auto_now=True)