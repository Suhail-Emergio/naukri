from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
personal_api = Router(tags=['personal'])
employment_api = Router(tags=['employment'])
professional_api = Router(tags=['professional'])

@personal_api.post("/", response={201: PersonalData, 409: Message}, description="User personal data creation")
async def personal(request, data: PersonalCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    personal = await Personal.objects.acreate(**data_dict)
    return 201, personal

@personal_api.get("/", response={200: List[PersonalData], 409: Message}, description="User personal data")
async def personal_data(request):
    personal = [i async for i in Personal.objects.filter(user=request.auth)]
    return 200, personal

@employment_api.post("/", response={201: EmploymentData, 409: Message}, description="User employment data creation")
async def employment(request, data: EmploymentCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    employment = await Employment.objects.acreate(**data_dict)
    return 201, employment

@employment_api.get("/", response={200: List[EmploymentData], 409: Message}, description="User employment data")
async def employment_data(request):
    employment = [i async for i in Employment.objects.filter(user=request.auth)]
    return 200, employment

@professional_api.post("/", response={201: ProfessionalData, 409: Message}, description="User professional data creation")
async def professional(request, data: ProfessionalCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    professional = await Professional.objects.acreate(**data_dict)
    return 201, professional

@professional_api.get("/", response={200: List[ProfessionalData], 409: Message}, description="User professional data")
async def professional_data(request):
    professional = [i async for i in Professional.objects.filter(user=request.auth)]
    return 200, professional