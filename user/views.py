from ninja import Router, PatchDict
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
from naukry.utils.twilio import whatsapp_message
import random
from django.core.cache import cache

user_api = Router(tags=['user'])
User = get_user_model()

#################################  R E G I S T E R  &  L O G I N  #################################
@user_api.post("/register", auth=None, response={201: Message, 409: Message}, description="User creation")
async def register(request, data: UserCreation):
    if not await User.objects.filter(Q(username=data.phone) | Q(email=data.email)).aexists():
        user = await User.objects.acreate(**data.dict(), username=data.phone)
        user.set_password(data.password)
        await user.asave()
        otp = random.randint(1111,9999)
        key = f'otp_{data.phone}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        await whatsapp_message(otp, data.phone)
        refresh = RefreshToken.for_user(user)
        return 201, {"message": "Otp send successfully"}
    return 409, {"message": "User already exists"}

@user_api.post("/mobile_login", auth=None, response={200: Message, 403: Message, 401: Message}, description="Authenticate user with username and password")
async def mobile_login(request, data: LoginSchema):
    if await User.objects.filter(username=data.username).aexists():
        user = await User.objects.aget(username=data.username)
        if user.phone_verified:
            if user.role == "recruiter" and user.subscribed == False:
                return 403, {"message": "Please subscribe to a plan"}
            otp = random.randint(1111,9999)
            key = f'otp_{user.username}'
            cache_value = await sync_to_async(cache.get)(key)
            if cache_value:
                await sync_to_async(cache.delete)(key)
            await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
            await whatsapp_message(otp, user.username)
            return 200, {"message": "Otp send successfully"}
        return 403, {"message": "Mobile not verified"}
    return 401, {"message": "Invalid credentials"}

@user_api.post("/email_login", auth=None, response={200: TokenSchema, 403: Message, 401: Message}, description="Authenticate user with email and password/ Social login using email only")
async def email_login(request, data: LoginSchema):
    if await User.objects.filter(email=data.username).aexists():
        user = await User.objects.aget(email=data.username)
        if user.role == "recruiter" and user.subscribed == False:
            return 403, {"message": "Please subscribe to a plan"}
        if user.phone_verified:
            refresh = RefreshToken.for_user(user)
            if data.password:
                if user.email_verified:
                    if check_password(data.password, user.password):
                        return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
                return 403, {"message": "Email not verified for login"}

            ## SOCIAL LOGIN
            else:
                user.email_verified = True
                await user.asave()
                return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
            return 401, {"message": "Invalid credentials"}
        return 403, {"message": "Verify your account to continue login"}
    return 401, {"message": "Invalid credentials"}

#################################  V E R I F I C A T I O N S  #################################
@user_api.post("/mobile_otp_verify", auth=None, response={200: TokenSchema, 401: Message, 403: Message}, description="Verify OTP using mobile number")
async def mobile_otp_verify(request, data: MobileOtpVerify):
    key = f'otp_{data.phone}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        if cache_value == data.otp:
            user = await User.objects.aget(phone=data.phone)
            if not user.phone_verified:
                user.phone_verified = True
                await user.asave()
            refresh = RefreshToken.for_user(user)
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}

@user_api.post("/retry_otp", auth=None, response={201: Message, 401: Message, 403: Message}, description="Retry sending OTP using mobile number")
async def retry_otp(request, data: ForgotPassword):
    if await User.objects.filter(phone=data.phone).aexists():
        user = await User.objects.aget(phone=data.phone)
        verified = await sync_to_async(lambda: user.phone_verified)()
        if not verified:
            otp = random.randint(1111,9999)
            key = f'otp_{data.phone}'
            cache_value = await sync_to_async(cache.get)(key)
            if cache_value:
                await sync_to_async(cache.delete)(key)
            await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
            await whatsapp_message(otp, data.phone)
            return 201, {"message": "Otp send successfully"}
        return 403, {"message": "Mobile already verified"}
    return 401, {"message": "User not registered"}

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
            user.email_verified = True
            await user.asave()
            refresh = RefreshToken.for_user(user)
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
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
@user_api.get("/", response={200: UserData, 409: Message}, description="Get info of logged user")
async def get_user(request):
    user = request.auth
    return 200, user

@user_api.patch("/", response={200: Message, 400: Message, 409: Message}, description="Update user information")
async def update_user(request, data: PatchDict[UserCreation]):
    user = request.auth
    for attr, value in data.items():
        setattr(user, attr, value)

    ## Verify Phone
    if 'phone' in data:
        otp = random.randint(1111,9999)
        key = f'otp_{data.phone}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        await whatsapp_message(otp, data.phone)

    ## Hashing password
    if 'password' in data:
        if check_password(data['password'], user.password):
            return 400, {"message": "New password can't be same as old password"}
        user.set_password(data['password'])
    await user.asave()
    return 200, {"message": "Account Updated Successfully"}

@user_api.delete("/", response={200: Message, 409: Message}, description="Delete user account")
async def delete_user(request):
    user = request.auth
    await user.adelete()
    return 200, {"message": "Account Deleted Successfully"}

#################################  F O R G O T  P A S S W O R D  #################################
@user_api.post("/forgot_password", response={200: Message, 401: Message}, description="Send otp to user mobile to change password")
async def forgot_pwd(request, data: ForgotPassword):
    if await User.objects.filter(phone=data.phone).aexists():
        user = await User.objects.aget(phone=data.phone)
        otp = random.randint(1111,9999)
        key = f'change_pwd_{data.phone}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        await whatsapp_message(otp, data.phone)
        return 200, {"message": "OTP sent to mobile"}
    return 401, {"message": "User not found"}

@user_api.post("/change_password", response={200: Message, 400: Message, 401: Message, 403: Message}, description="Change password using OTP")
async def change_pwd(request, data: ResetPassword):
    key = f'change_pwd_{data.phone}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        if int(cache_value) == data.otp:
            if check_password(data.password, user.password):
                return 400, {"message": "New password can't be same as old password"}
            user = await User.objects.aget(phone=data.phone)
            user.set_password(data.password)
            await user.asave()
            return 200, {"message": "Password changed successfully"}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}