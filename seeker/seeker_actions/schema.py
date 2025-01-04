from ninja import Schema
from typing import *
from ninja.orm import create_schema
from jobs.jobposts.schema import JobData
from .models import *

class JobInvitations(Schema):
    job: JobData
    read : bool