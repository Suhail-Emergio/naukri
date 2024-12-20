from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q

User = get_user_model()
details_api = Router(tags=['details'])

@details_api.post("/personal", response={201: PersonalData, 409: Message}, description="User personal data creation")
async def personal(request, data: PersonalCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    personal = await Personal.objects.acreate(**data_dict)
    return 201, personal

@details_api.patch("/personal", response={200: PersonalData, 404: Message, 409: Message}, description="User personal data update")
async def update_personal_data(request, data: PersonalCreation):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        for attr, value in data.dict().items():
            setattr(personal, attr, value)
        await personal.asave()
        return 200, personal
    return 404, {"message": "Personal data not found"}

@details_api.get("/personal", response={200: List[PersonalData], 409: Message}, description="User personal data")
async def personal_data(request):
    personal = [i async for i in Personal.objects.filter(user=request.auth)]
    return 200, personal

@details_api.post("/employment", response={201: EmploymentData, 409: Message}, description="User employment data creation")
async def employment(request, data: EmploymentCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    employment = await Employment.objects.acreate(**data_dict)
    return 201, employment

@details_api.patch("/employment", response={200: EmploymentData, 404: Message, 409: Message}, description="User employment data update")
async def update_employment_data(request, data: EmploymentCreation):
    if await Employment.objects.filter(user=request.auth).aexists():
        employment = await Employment.objects.aget(user=request.auth)
        for attr, value in data.dict().items():
            setattr(employment, attr, value)
        await employment.asave()
        return 200, employment
    return 404, {"message": "Employment data not found"}

@details_api.get("/employment", response={200: List[EmploymentData], 409: Message}, description="User employment data")
async def employment_data(request):
    employment = [i async for i in Employment.objects.filter(user=request.auth)]
    return 200, employment

@details_api.post("/professional", response={201: ProfessionalData, 409: Message}, description="User professional data creation")
async def professional(request, data: ProfessionalCreation):
    data_dict = data.dict()
    data_dict['user'] = request.auth
    professional = await Professional.objects.acreate(**data_dict)
    return 201, professional

@details_api.patch("/professional", response={200: ProfessionalData, 404: Message, 409: Message}, description="User professional data update")
async def update_professional_data(request, data: ProfessionalCreation):
    if await Professional.objects.filter(user=request.auth).aexists():
        professional = await Professional.objects.aget(user=request.auth)
        for attr, value in data.dict().items():
            setattr(professional, attr, value)
        await professional.asave()
        return 200, professional
    return 404, {"message": "Professional data not found"}

@details_api.get("/professional", response={200: List[ProfessionalData], 409: Message}, description="User professional data")
async def professional_data(request):
    professional = [i async for i in Professional.objects.filter(user=request.auth)]
    return 200, professional