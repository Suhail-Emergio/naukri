from django.db import models
from django.contrib.auth import get_user_model
from recruiter.company.models import CompanyDetails as Company

User = get_user_model()

class Suggestions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.TextField()
    created_on = models.DateTimeField(auto_now=True)