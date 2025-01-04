from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from .utils.auth import *
from user.views import *
from jobs.jobposts.views import jobs_api
from jobs.based_jobs.views import based_jobs_api
from jobs.job_actions.views import job_actions_api
from recruiter.company.views import company_api
from recruiter.recruiter_actions.views import recruiter_actions_api
from seeker.details.views import *
from seeker.seeker_actions.views import seeker_actions_api

api = NinjaAPI(auth=AsyncJWTAuth())

## User API
api.add_router('user', user_api)

## Seeker API
api.add_router('details', details_api)
api.add_router('seeker_actions', seeker_actions_api)

## Recruiter API
api.add_router('company', company_api)
api.add_router('recruiter_actions', recruiter_actions_api)

## Jobs API
api.add_router('jobs', jobs_api)
api.add_router('based-jobs', based_jobs_api)
api.add_router('job-actions', job_actions_api)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)