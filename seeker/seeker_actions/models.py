from django.db import models
from django.contrib.auth import get_user_model
from recruiter.company.models import CompanyDetails

User = get_user_model()

class BlockedCompanies(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE)
    blocked_on = models.DateTimeField(auto_now=True)