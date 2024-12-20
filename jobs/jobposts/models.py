from django.db import models
# from django.contrib.auth import get_user_model
from recruiter.company.models import CompanyDetails as Company

# User = get_user_model()

class JobPosts(models.Model):
    ## Job Details
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.JSONField()
    type = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    vacancy = models.IntegerField()
    industry = models.CharField(max_length=250)
    functional_area = models.CharField(max_length=250)

    ## Preffered Employee Details
    gender = models.CharField(max_length=50, choices=[('male', 'male'), ('female', 'female')], null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    experience_min = models.IntegerField(null=True, blank=True)
    experience_max = models.IntegerField(null=True, blank=True)
    candidate_location = models.CharField(max_length=50, null=True, blank=True)
    education = models.CharField(max_length=50, null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)