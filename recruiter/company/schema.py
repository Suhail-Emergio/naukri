from ninja import Schema
from typing import *
from ninja.orm import create_schema
from .models import *

# Company Details Schema
class CompanyCreation(Schema):
    name: str
    about : str
    website : str
    functional_area : str
    address : Union[List[str], Dict[str, Any]]
    city : str
    state : str
    postal_code : str
    pan_no : str
    gst_no : str
    mca_no : Optional[str] = None

CompanyData = create_schema(CompanyDetails)