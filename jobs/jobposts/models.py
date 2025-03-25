from django.db import models
from recruiter.company.models import CompanyDetails as Company
from datetime import date

# class JobPosts(models.Model):
#     ## Job Details
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
#     title = models.CharField(max_length=250)
#     description = models.TextField(default="")
#     requirements = models.TextField(default="")
#     roles = models.TextField(default="")
#     benefits = models.TextField(default="")
#     type = models.CharField(max_length=250) # `Full-time, Part-time, Contract, Internship`
#     category = models.CharField(max_length=250, choices=[('remote', 'remote'), ('onsite', 'onsite'), ('hybrid', 'hybrid')], default='remote') # Remote, Onsite, Hybrid
#     city = models.CharField(max_length=250, default='')
#     country = models.CharField(max_length=250)
#     vacancy = models.IntegerField()
#     industry = models.CharField(max_length=250)
#     functional_area = models.CharField(max_length=250)
#     created_on = models.DateTimeField(auto_now=True)
#     expire_on = models.DateField(default=date.today)
#     active = models.BooleanField(default=True)
#     views = models.IntegerField(default=0)

#     ## Preffered Employee Details
#     gender = models.CharField(max_length=50, choices=[('male', 'male'), ('female', 'female')], null=True, blank=True)
#     nationality = models.CharField(max_length=50, null=True, blank=True)
#     experience_min = models.IntegerField(null=True, blank=True)
#     experience_max = models.IntegerField(null=True, blank=True)
#     candidate_location = models.JSONField(null=True, blank=True)
#     education = models.CharField(max_length=50, null=True, blank=True)
#     salary_min = models.IntegerField(null=True, blank=True)
#     salary_max = models.IntegerField(null=True, blank=True)
#     currency = models.CharField(max_length=50, default='INR')
#     skills = models.JSONField(null=True, blank=True)
#     custom_qns = models.JSONField(null=True, blank=True)


class JobPosts(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=250)
    description = models.TextField(default="")
    city = models.CharField(max_length=250, default='')
    country = models.CharField(max_length=250)
    location_type = models.JSONField(null=True, blank=True) # `Remote, Onsite, Hybrid`
    address = models.TextField(null=True, blank=True)
    type = models.JSONField(null=True, blank=True) # `Full-time, Part-time, Contract, Internship`
    schedule = models.JSONField(null=True, blank=True) # `Day, Night, Evening, Rotational`
    start_date = models.DateField(null=True, blank=True)
    vacancy = models.IntegerField(default=0)
    timeline = models.CharField(max_length=200, null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    salary_period = models.CharField(max_length=50, default="per year")
    benefits = models.JSONField(null=True, blank=True)
    supplimental_pay = models.JSONField(null=True, blank=True)
    application_updations_email = models.JSONField(null=True, blank=True)
    resume_required = models.BooleanField(default=True)
    end_date = models.DateField(null=True, blank=True)
    skills = models.JSONField(null=True, blank=True)
    pro_experience = models.FloatField(null=True, blank=True)
    experience = models.FloatField(null=True, blank=True)
    education = models.CharField(max_length=50, null=True, blank=True)
    custom_qns = models.JSONField(null=True, blank=True)
    languages = models.JSONField(null=True, blank=True)
    prefered_work_loc = models.JSONField()
    commute = models.BooleanField(default=False)
    relocate = models.BooleanField(default=False)
    date_availablity = models.BooleanField(default=True)
    gender = models.CharField(max_length=50, choices=[('male', 'male'), ('female', 'female')], null=True, blank=True)
    created_on = models.DateTimeField(auto_now=True)
    expire_on = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    views = models.IntegerField(default=0)