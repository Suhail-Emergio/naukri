from ninja import Router
from django.contrib.auth import get_user_model
from jobs.jobposts.schema import *
from typing import *
from jobs.jobposts.models import *
from user.schema import *
from django.db.models import Q

# async def apply_jobs(request):
# async def applied_jobs(request):
# async def save_jobs(request):
# async def invited_jobs(request):
# async def search_jobs(request):
# async def filter_jobs(request):