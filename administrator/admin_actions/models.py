from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class Plans(models.Model):
    title = models.CharField(max_length=30)
    description = models.JSONField()
    duration = models.DurationField()
    posts = models.IntegerField(null=True, blank=True)
    duration = models.DurationField(default=timedelta(days=30))
    audience = models.CharField(max_length=20, choices=[('seeker','seeker'), ('recruiter','recruiter')], default="seeker")
    rate = models.IntegerField()
    feature = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now=True)

class Banner(models.Model):
    image = models.ImageField(upload_to="banner")