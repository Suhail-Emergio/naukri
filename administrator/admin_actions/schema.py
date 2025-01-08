from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

PlanData = create_schema(Plans)
BannerData = create_schema(Banner)