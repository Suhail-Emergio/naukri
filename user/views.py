from ninja import Router
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from ninja_jwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q
from ninja.responses import codes_4xx
from asgiref.sync import sync_to_async
from ninja_jwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password

user_api = Router(tags=['user'])
User = get_user_model()

@user_api.post("/register", auth=None, response={201: TokenSchema, 409: Message}, description="User creation")
async def register(request, data: UserCreation):
    if not await User.objects.filter(Q(username=data.username) | Q(email=data.email)).aexists():
        user = await User.objects.acreate(**data.dict())
        user.set_password(data.password)
        await user.asave()
        refresh = RefreshToken.for_user(user)
        return 201, {'access': str(refresh.access_token), 'refresh': str(refresh)}
    return 409, {"message": "User already exists"}

@user_api.post("/mobile_login", auth=None, response={200: TokenSchema, 401: Message}, description="Authenticate user with username and password")
async def mobile_login(request, data: MobileLogin):
    user = await sync_to_async(authenticate)(username=data.username, password=data.password)
    if not user:
        return 401, {"message": "Invalid credentials"}
    refresh = RefreshToken.for_user(user)
    return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}

@user_api.post("/email_login", auth=None, response={200: TokenSchema, 401: Message}, description="Authenticate user with email and password/ Social login using email only")
async def email_login(request, data: EmailLogin):
    if await User.objects.filter(email=data.email).aexists():
        user = await User.objects.aget(email=data.email)
        if password:
            if check_password(data.password, user.password):
                refresh = RefreshToken.for_user(user)
                return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
        else:
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
    return 401, {"message": "Invalid credentials"}

@user_api.post("/refresh", auth=None, response={200: TokenSchema, 401: Message}, description="Refresh AccessToken using RefreshToken")
def refresh_token(request, token_data: TokenRefreshSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {'access': str(refresh.access_token),'refresh': str(refresh)}
    except Exception:
        return 401, {"message": "Invalid refresh token"}

@user_api.get("/", response={200: UserData, 401: Message}, description="Get info of logged user")
async def user(request):
    user = request.user
    return 200, user