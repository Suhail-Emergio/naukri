from ninja import Router
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from typing import *
from user.schema import *
from django.db.models.functions import ExtractMonth, TruncDate, ExtractDay
from jobs.job_actions.schema import ApplyJobs, ApplyCandidatesData
from recruiter.recruiter_actions.models import InterviewSchedule

User = get_user_model()
admin_api = Router(tags=['admin'])

#################################  D A S H B O A R D  #################################
@admin_api.get("/dashboard", response={200: List[AllUsers], 409: Message}, description="All users (id, name, and phone number)")
def dashboard(request):
    user = request.auth
    if user.is_superuser:
        application_count = get_active_jobs() ## Daily applications, and shortlisted count
        top_applications = get_top_applications() ## 4 jobs with top applications 
        total_applications = get_total_applications() ## Total applications, shortlisted, rejected, and pending count
        new_applications = get_new_applications() ## New applications
        interviews_scheduled = get_schedule_interviews() ## Interviews scheduled
        return {
            "application_count": application_count,
            "top_applications": top_applications,
            "total_applications": total_applications,
            "new_applications": new_applications,
            "interviews_scheduled": interviews_scheduled
        }
    return 409, {"message" : "You are not authorized to access users"}

def get_active_jobs():
    start_date = TruncWeek(start_date, week_start=1)
    count = (
        ApplyJobs.objects.filter(date__range=[start_date, today])
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(application_count=Count('id'), shortlisted_count=Count(Case(When(status='shortlisted', then=1))))
        .order_by("day")
    )
    return count

def get_top_applications():
    top_applications = (
        ApplyJobs.objects.values('job__name', 'job__company__name')
        .annotate(application_count=Count('id'))
        .order_by('-application_count')[:4]
    )
    return top_applications

def get_total_applications():
    total_applications = ApplyJobs.objects.all()
    return {
        "applications": total_applications.count(),
        "shortlisted": total_applications.filter(status='shortlisted').count(),
        "rejected": total_applications.filter(status='rejected').count(),
        "pending": total_applications.filter(status='applied').count()
    }

def get_new_applications():
    new_applications = ApplyJobs.objects.all().order_by('-created_on')[:5]
    return new_applications

def get_schedule_interviews():
    interviews = InterviewSchedule.objects.all().order_by('-created_on')[:5]
    return interviews