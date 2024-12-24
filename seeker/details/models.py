from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Personal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    intro = models.CharField(max_length=250)
    employed = models.BooleanField(default=False)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    cv = models.FileField(upload_to="details/resume/", null=True, blank=True)
    profile_image = models.ImageField(upload_to="details/profile/", null=True, blank=True)
    skills = models.JSONField()
    prefered_salary_pa = models.IntegerField()
    prefered_work_loc = models.JSONField()

class Employment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiance = models.IntegerField()
    job_title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200)
    duration = models.IntegerField()
    ctc = models.IntegerField()
    notice_pd = models.IntegerField()
    department = models.CharField(max_length=200)
    job_role = models.CharField(max_length=500)
    role_category = models.CharField(max_length=500)

class Qualification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    education = models.CharField(max_length=150)
    course = models.CharField(max_length=200)
    type_course = models.CharField(max_length=200)
    specialisation = models.CharField(max_length=200)
    university = models.CharField(max_length=200)
    starting_yr = models.IntegerField()
    ending_yr = models.IntegerField()
    grade = models.IntegerField()

class Preference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=150)
    job_shift = models.CharField(max_length=150)
    job_role = models.JSONField()
    pref_salary = models.IntegerField()
    job_location = models.JSONField()