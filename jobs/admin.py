from django.contrib import admin
from jobs.job_actions.models import ApplyJobs, SaveJobs
from jobs.jobposts.models import JobPosts

admin.site.register(JobPosts)
admin.site.register(ApplyJobs)
admin.site.register(SaveJobs)