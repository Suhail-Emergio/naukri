from ninja import Router, PatchDict, File, UploadedFile
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
company_api = Router(tags=['company'])

#################################  C O M P A N Y  D A T A S  #################################
@company_api.post("/", response={201: CompanyData, 401: Message, 409:Message}, description="Company data creation")
async def company_creation(request, data: CompanyCreation, logo: UploadedFile = File(...)):
    if request.auth.role == "recruiter" and not await CompanyDetails.objects.filter(user=request.auth).aexists():
        company = await CompanyDetails.objects.acreate(**data.dict(), user=request.auth)
        await company.logo.asave(logo.name, logo)
        return 201, company
    return 401, {"message": "Not Authorised"}

@company_api.post("/company/logo", response={201: Message, 404: Message}, description="Upload or update company logo")
async def update_logo(request, logo: UploadedFile = File(...)):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        personal.logo = logo
        await personal.asave()
        return 201, {"message": "logo updated successfully"}
    return 404, {"message": "Personal data not found"}

@company_api.patch("/edit", response={201: CompanyData, 404: Message, 409: Message}, description="Company data update")
async def update_company(request, data: PatchDict[CompanyData]):
    if await CompanyDetails.objects.filter(user=request.auth).aexists():
        company = await CompanyDetails.objects.aget(user=request.auth)
        for attr, value in data.items():
            setattr(company, attr, value)
        await company.asave()
        return 201, company
    return 404, {"message": "Company data not found"}

@company_api.get("/", response={200: CompanyData, 404: Message, 409: Message}, description="Company data of logged user")
async def company(request):
    if await CompanyDetails.objects.filter(user=request.auth).aexists():
        comp = await CompanyDetails.objects.aget(user=request.auth)
        return 200, comp
    return 404, {"message" : "No company details found"}

@company_api.get("/all_company", response={200: List[CompanyData], 409: Message}, description="Company data of all posts")
async def all_company(request):
    comp = [i async for i in CompanyDetails.objects.all()]
    return 200, comp