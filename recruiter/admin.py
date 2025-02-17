from django.contrib import admin
from recruiter.recruiter_actions.models import InterviewSchedule
from recruiter.company.models import CompanyDetails

admin.site.register(CompanyDetails)
admin.site.register(InterviewSchedule)