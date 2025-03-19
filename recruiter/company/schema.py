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
    country : str
    postal_code : str
    contact_name : str
    contact_land_number : str
    contact_mobile_number : str
    designation : str

CompanyData = create_schema(CompanyDetails)