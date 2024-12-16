from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

class PersonalCreation(Schema):
    user : int
    intro : str
    city : str
    state : str
    cv : Optional[str] = None
    skills : List[str]
    prefered_salary_pa : int
    prefered_work_loc : str

PersonalData = create_schema(Personal)