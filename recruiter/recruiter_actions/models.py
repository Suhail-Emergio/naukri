from django.db import models
from django.contrib.auth import get_user_model
from seeker.details.models import Personal
from jobs.jobposts.models import JobPosts

User = get_user_model()

class SaveCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)

class InviteCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosts, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    interested = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now=True)