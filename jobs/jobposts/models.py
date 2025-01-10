from django.db import models
from recruiter.company.models import CompanyDetails as Company
from datetime import date

class JobPosts(models.Model):
    ## Job Details
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField(default="")
    requirements = models.TextField(default="")
    roles = models.TextField(default="")
    benefits = models.TextField(default="")
    type = models.CharField(max_length=250) # `Full-time, Part-time, Contract, Internship`
    category = models.CharField(max_length=250, choices=[('remote', 'remote'), ('onsite', 'onsite'), ('hybrid', 'hybrid')], default='remote') # Remote, Onsite, Hybrid
    city = models.CharField(max_length=250, default='')
    country = models.CharField(max_length=250)
    vacancy = models.IntegerField()
    industry = models.CharField(max_length=250)
    functional_area = models.CharField(max_length=250)
    created_on = models.DateTimeField(auto_now=True)
    expire_on = models.DateField(default=date.today)

    ## Preffered Employee Details
    gender = models.CharField(max_length=50, choices=[('male', 'male'), ('female', 'female')], null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    experience_min = models.IntegerField(null=True, blank=True)
    experience_max = models.IntegerField(null=True, blank=True)
    candidate_location = models.JSONField(null=True, blank=True)
    education = models.CharField(max_length=50, null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=50, default='INR')
    skills = models.JSONField(null=True, blank=True)
    custom_qns = models.JSONField(null=True, blank=True)