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
from naukry.utils.email import send_mails
import random
from django.core.cache import cache

user_api = Router(tags=['user'])
User = get_user_model()

#################################  R E G I S T E R  &  L O G I N  #################################
@user_api.post("/register", auth=None, response={201: TokenSchema, 409: Message}, description="User creation")
async def register(request, data: UserCreation):
    if not await User.objects.filter(Q(username=data.phone) | Q(email=data.email)).aexists():
        data_dict = data.dict()
        data_dict['username'] = data.phone
        user = await User.objects.acreate(**data_dict)
        user.set_password(data.password)
        await user.asave()
        otp = random.randint(1111,9999)
        key = f'otp_{data.phone}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        refresh = RefreshToken.for_user(user)
        return 201, {'access': str(refresh.access_token), 'refresh': str(refresh)}
    return 409, {"message": "User already exists"}

@user_api.post("/mobile_login", auth=None, response={200: TokenSchema, 403: Message, 401: Message}, description="Authenticate user with username and password")
async def mobile_login(request, data: MobileLogin):
    user = await sync_to_async(authenticate)(username=data.username, password=data.password)
    if not user:
        return 401, {"message": "Invalid credentials"}
    # if user.mobile_verified:
        refresh = RefreshToken.for_user(user)
        return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
    # return 403, {"message": "Mobile not verified"}

@user_api.post("/email_login", auth=None, response={200: TokenSchema, 403: Message, 401: Message}, description="Authenticate user with email and password/ Social login using email only")
async def email_login(request, data: EmailLogin):
    if await User.objects.filter(email=data.email).aexists():
        user = await User.objects.aget(email=data.email)
        # if user.mobile_verified:
        refresh = RefreshToken.for_user(user)
        if data.password:
            if check_password(data.password, user.password):
                return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
        else:
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
        # return 403, {"message": "Mobile not verified"}
    return 401, {"message": "Invalid credentials"}

#################################  V E R I F I C A T I O N S  #################################
@user_api.post("/mobile_verify", auth=None, response={200: TokenSchema, 401: Message, 403: Message}, description="Verify OTP using mobile number")
async def mobile_verify(request, data: MobileOtpVerify):
    key = f'otp_{data.phone}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        if cache_value == data.otp:
            user = await User.objects.aget(phone=data.phone)
            refresh = RefreshToken.for_user(user)
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}

@user_api.post("/send_email_otp", response={200: Message}, description="Send OTP to email")
async def send_email_otp(request):
    user = request.auth
    otp = random.randint(1111,9999)
    key = f'email_otp_{user.email}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        await sync_to_async(cache.delete)(key)
    await send_mails(user.email, user.name, f"{otp:04d}")
    await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
    return 200, {"message": "OTP sent to email"}

@user_api.post("/email_verify", response={200: TokenSchema, 401: Message, 403: Message}, description="Verify OTP using email")
async def email_verify(request, data: EmailOtpVerify):
    user = request.auth
    key = f'email_otp_{user.email}'
    cache_value = await cache.aget(key)
    if cache_value:
        if int(cache_value) == data.otp:
            refresh = RefreshToken.for_user(user)
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh)}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}

#################################  T O K E N  R E F R E S H  #################################
@user_api.post("/refresh", auth=None, response={200: TokenSchema, 401: Message}, description="Refresh AccessToken using RefreshToken")
def refresh_token(request, token_data: TokenRefreshSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {'access': str(refresh.access_token),'refresh': str(refresh)}
    except Exception:
        return 401, {"message": "Invalid refresh token"}

#################################  U S E R  D A T A  #################################
@user_api.get("/", response={200: UserData, 401: Message}, description="Get info of logged user")
async def user(request):
    user = request.auth
    return 200, user

@user_api.delete("/", response={200: Message, 401: Message}, description="Delete user account")
async def user(request):
    user = request.auth
    await user.adelete()
    return 200, {"message": "Account Deleted Successfully"}

# async def forgot_pwd(request):
# async def change_pwd(request):
# async def user(request): Patch