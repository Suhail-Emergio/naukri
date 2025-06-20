from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Personal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    intro = models.TextField()
    employed = models.BooleanField(default=False)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    nationality = models.CharField(max_length=250, null=True, blank=True)
    gender = models.CharField(max_length=250, null=True, blank=True)
    address = models.JSONField(null=True, blank=True)
    differently_abled = models.BooleanField(default=False)
    dob = models.DateField(null=True, blank=True)
    cv = models.FileField(upload_to="details/resume/", null=True, blank=True)
    profile_image = models.ImageField(upload_to="details/profile/", null=True, blank=True)
    skills = models.JSONField()
    languages = models.JSONField(null=True, blank=True)
    certificates = models.JSONField(null=True, blank=True)
    projects = models.JSONField(null=True, blank=True)
    prefered_salary_pa = models.IntegerField()
    prefered_work_loc = models.JSONField()
    total_experience_years = models.IntegerField(default=0)
    total_experience_months = models.IntegerField(default=0)
    immediate_joiner = models.BooleanField(default=False)
    work_availability = models.BooleanField(default=True)

class Employment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiance = models.IntegerField()
    job_title = models.CharField(max_length=150)
    company_name = models.CharField(max_length=200)
    duration = models.IntegerField()
    ctc = models.IntegerField()
    notice_pd = models.IntegerField()
    department = models.CharField(max_length=200)
    industry = models.CharField(max_length=200, default='')
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
    grade = models.FloatField(default=0.0)

class Preference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.JSONField()
    employment_type = models.JSONField()
    job_shift = models.JSONField()
    job_role = models.JSONField()
    pref_salary = models.IntegerField()
    job_location = models.JSONField()

class SearchApps(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)
    count = models.IntegerField(default=0)

class NotificationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendations = models.CharField(max_length=50, choices=[('daily','daily'), ('weekly','weekly'), ('ban','ban')], default="daily")
    alerts = models.CharField(max_length=50, choices=[('daily','daily'), ('weekly','weekly'), ('ban','ban')], default="daily")
    mobile_notifications = models.BooleanField(default=True)
    messages_recruiter = models.CharField(max_length=50, choices=[('immediately','immediately'), ('ban','ban')], default="immediately")
    applications = models.CharField(max_length=50, choices=[('daily','daily'), ('ban','ban')], default="daily")
    promotions = models.CharField(max_length=50, choices=[('daily','daily'), ('ban','ban')], default="daily")