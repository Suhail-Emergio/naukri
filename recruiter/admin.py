from django.contrib import admin
from recruiter.recruiter_actions.models import *
from recruiter.company.models import CompanyDetails

admin.site.register(CompanyDetails)
admin.site.register(InterviewSchedule)
admin.site.register(SaveCandidate)
admin.site.register(InviteCandidate)
admin.site.register(EmailTemplate)