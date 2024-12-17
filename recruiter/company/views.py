from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
company_api = Router(tags=['company'])

@company_api.post("/", response={201: CompanyData, 401: Message, 409:Message}, description="Company data creation")
async def job(request, data: CompanyCreation):
    data_dict = data.dict()
    if request.auth.role == "recruiter":
        data_dict['user'] = request.auth
        company = await CompanyDetails.objects.acreate(**data_dict)
        return 201, company
    return 401, {"message": "Not Authorised"}

@company_api.get("/", response={200: List[CompanyData], 409: Message}, description="Company data of logged user")
async def company(request):
    comp = [i async for i in CompanyDetails.objects.filter(user=request.auth)]
    return 200, comp

@company_api.get("/all_company", response={200: List[CompanyData], 409: Message}, description="Company data of all posts")
async def all_company(request):
    comp = [i async for i in CompanyDetails.objects.all()]
    return 200, comp