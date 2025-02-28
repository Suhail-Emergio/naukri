from ninja import Router
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from typing import *
from user.schema import *
from django.db.models.functions import ExtractMonth, TruncDate, ExtractDay, TruncWeek
from jobs.job_actions.schema import ApplyJobs, ApplyCandidatesData
from recruiter.recruiter_actions.models import InterviewSchedule
from seeker.details.models import Personal
from datetime import date, timedelta
from django.db.models import Count, Case, When, DateField
from django.db.models.functions import Cast

User = get_user_model()
admin_dashboard_api = Router(tags=['dashboard'])

#################################  D A S H B O A R D  #################################
@admin_dashboard_api.get("/dashboard", description="All users (id, name, and phone number)")
def dashboard(request): 
    user = request.auth
    if user and user.is_superuser:
        application_count = list(get_active_jobs().values()) ## Daily applications, and shortlisted count
        top_applications = list(get_top_applications().values()) ## 4 jobs with top applications 
        total_applications = get_total_applications() ## Total applications, shortlisted, rejected, and pending count
        new_applications = list(get_new_applications().values()) ## New applications
        interviews_scheduled = list(get_schedule_interviews().values()) ## Interviews scheduled
        return {
            "application_count": application_count,
            "top_applications": top_applications,
            "total_applications": total_applications,
            "new_applications": new_applications,
            "interviews_scheduled": interviews_scheduled
        }
    return 403, {"message" : "You are not authorized to access users"}

def get_active_jobs():
    today = date.today()
    start_date = today - timedelta(days=today.weekday())
    count = (
        ApplyJobs.objects.filter(created_on__gte=start_date, created_on__lte=today)
        .annotate(day=Cast('created_on', DateField()))
        .values("day")
        .annotate(
            application_count=Count('id'),
            shortlisted_count=Count(Case(When(status='shortlisted', then=1)))
        )
        .order_by("day")
    )
    data_dict = {
        entry['day']: {
            'application_count': entry['application_count'],
            'shortlisted_count': entry['shortlisted_count'],
            'date': entry['day'].day
        } for entry in count if entry['day'] is not None
    }
    result = {}
    current_date = start_date
    while current_date <= today:
        date_key = current_date.strftime('%d-%m-%y')
        if current_date in data_dict:
            result[date_key] = data_dict[current_date]
        else:
            result[date_key] = {
                'application_count': 0,
                'shortlisted_count': 0,
                'date': current_date.day
            }
        current_date += timedelta(days=1)
    return result

def get_top_applications():
    top_applications = (
        ApplyJobs.objects.values('job__title', 'job__company__name', 'id')
        .annotate(application_count=Count('id'))
        .order_by('-application_count')[:4]
    )
    return {
        entry['id']: {
            'application_count': entry['application_count'],
            'title': entry['job__title'],
            'company': entry['job__company__name']
        }
        for entry in top_applications
    }

def get_total_applications():
    total_applications = ApplyJobs.objects.all()
    return [{
        "applications": total_applications.count(),
        "shortlisted": total_applications.filter(status='shortlisted').count(),
        "rejected": total_applications.filter(status='rejected').count(),
        "pending": total_applications.filter(status='applied').count()
    }]

def get_new_applications():
    new_applications = ApplyJobs.objects.values('user').order_by('-created_on')[:5]
    apps = []
    for i in new_applications:
        user = User.objects.get(id=i['user'])
        name = user.name
        image = None
        if Personal.objects.filter(user=user).exists():
            personal = Personal.objects.get(user=user)
            image = personal.profile_image
        apps.append({
            "name": name,
            "image": image
        })
    return apps

def get_schedule_interviews():
    interviews = InterviewSchedule.objects.all().order_by('-created_on')[:5]
    return interviews