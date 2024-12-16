from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from ninja.responses import codes_4xx
from asgiref.sync import sync_to_async
from ninja_jwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password

personal_api = Router(tags=['personal'])
employment_api = Router(tags=['employment'])
professional_api = Router(tags=['professional'])
User = get_user_model()

@personal_api.post("/", response={201: PersonalData, 409: Message}, description="user personal data creation")
async def personal(request, data: PersonalCreation):
    data_dict = data.dict()
    user = await User.objects.aget(id=request.auth)
    data_dict['user'] = request.auth
    personal = await Personal.objects.acreate(**data_dict)
    return 201, personal

@personal_api.get("/", response={200: List[PersonalData], 409: Message}, description="user personal data creation")
async def personal_data(request):
    personal = [i async for i in Personal.objects.filter(user=request.auth)]
    return 200, personal