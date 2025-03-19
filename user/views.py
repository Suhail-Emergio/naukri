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
User = get_user_model()##  R E G I S T E R  &  L O G I N  #################################
@user_api.post("/register", auth=None, response={201: Message, 409: Message}, description="User creation")
async def register(request, data: UserCreation):
    if await User.objects.filter(Q(username=data.phone) | Q(email=data.email)).aexists():
        existing_user = await User.objects.aget(Q(username=data.phone) | Q(email=data.email))
        phone_verified = await sync_to_async(lambda: existing_user.phone_verified)()
        if phone_verified:
            return 409, {"message": "User already exists"}
        user = existing_user
    else:
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
        refresh = RefreshToken.for_user(user)
        if data.password:
            if user.email_verified:
                if check_password(data.password, user.password):
                    return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
                return 401, {"message": "Invalid credentials"}
            return 403, {"message": "Email not verified for login"}

        ## SOCIAL LOGIN
        else:
            user.email_verified = True
            await user.asave()
            return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
        return 401, {"message": "Invalid credentials"}
    return 401, {"message": "Invalid credentials"}

#################################  V E R I F I C A T I O N S  #################################
@user_api.post("/mobile_otp_verify", auth=None, response={200: TokenSchema, 203: Message, 401: Message, 403: Message}, description="Verify OTP using mobile number")
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
        otp = random.randint(1111,9999)
        key = f'otp_{data.phone}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        await whatsapp_message(otp, data.phone)
        return 201, {"message": "Otp send successfully"}
    return 401, {"message": "User not registered"}

@user_api.post("/send_email_otp", auth=None, response={200: Message}, description="Send OTP to email")
async def send_email_otp(request, data: EmailOtpVerify):
    if await User.objects.filter(email=data.email).aexists():
        user = await User.objects.aget(email=data.email)
        name = await sync_to_async(lambda: user.name)()
        otp = random.randint(1111,9999)
        key = f'email_otp_{data.email}'
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await send_mails(data.email, name, f"{otp:04d}")
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        return 200, {"message": "OTP sent to email"}
    return 401, {"message": "User not registered"}

@user_api.post("/email_verify", auth=None, response={200: TokenSchema, 401: Message, 403: Message}, description="Verify OTP using email")
async def email_verify(request, data: EmailOtpVerify):
    if await User.objects.filter(email=data.email).aexists():
        user = await User.objects.aget(email=data.email)
        key = f'email_otp_{data.email}'
        cache_value = await cache.aget(key)
        if cache_value:
            if int(cache_value) == data.otp:
                user.email_verified = True
                await user.asave()
                refresh = RefreshToken.for_user(user)
                return 200, {'access': str(refresh.access_token), 'refresh': str(refresh), 'role': user.role, "name": user.name}
            return 403, {"message": "Invalid OTP"}
        return 401, {"message": "OTP expired"}
    return 403, {"message": "User not registered"}

#################################  T O K E N  R E F R E S H  #################################
@user_api.post("/refresh", auth=None, response={200: TokenSchema, 401: Message}, description="Refresh AccessToken using RefreshToken")
def refresh_token(request, token_data: TokenRefreshSchema):
    try:
        refresh = RefreshToken(token_data.refresh)
        return 200, {'access': str(refresh.access_token),'refresh': str(refresh), 'role': "", "name": ""}
    except Exception:
        return 401, {"message": "Invalid refresh token"}

#################################  U S E R  D A T A  #################################
@user_api.get("/", response={200: UserData, 409: Message}, description="Get info of logged user")
async def get_user(request):
    user = request.auth
    return 200, user

@user_api.patch("/", response={200: Message, 202: Message, 400: Message, 405: Message, 409: Message}, description="Update user information")
async def update_user(request, data: PatchDict[UserCreation]):
    user = request.auth
    for attr, value in data.items():
        setattr(user, attr, value)

    ## Verify Phone
    if 'phone' in data:
        if await User.objects.filter(username=data['phone']).aexists():
            return 405, {"message": "User with same phone number already exists"}
        otp = random.randint(1111,9999)
        key = f"change_phone_{data['phone']}"
        cache_value = await sync_to_async(cache.get)(key)
        if cache_value:
            await sync_to_async(cache.delete)(key)
        await sync_to_async(cache.set)(key, f"{otp:04d}", timeout=60)
        await whatsapp_message(otp, data['phone'])
        return 202, {"message": "OTP send Successfully"}

    ## Hashing password
    if 'password' in data:
        if check_password(data['password'], user.password):
            return 400, {"message": "New password can't be same as old password"}
        user.set_password(data['password'])
    await user.asave()
    return 200, {"message": "Account Updated Successfully"}

@user_api.patch("/change_phone", response={200: Message, 401: Message, 409: Message}, description="Update phone information using otp")
async def change_phone(request, data: MobileOtpVerify):
    user = request.auth
    key = f'change_phone_{data.phone}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        if cache_value == data.otp:
            user.username = data.phone
            user.phone = data.phone
            await user.asave()
            return 200, {'message': "Phone number changed successfully"}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}
            

@user_api.patch("/onesignal", response={200: Message, 400: Message, 409: Message}, description="Update user information")
async def update_onesignal(request, onesignal_id: str):
    user = request.auth
    if user.onesignal_id == onesignal_id:
        return 400, {"message": "Same OneSignal ID"}
    user.onesignal_id = onesignal_id
    await user.asave()
    return 200, {"message": "OneSignal ID Updated Successfully"}

@user_api.delete("/", response={200: Message, 409: Message}, description="Delete user account")
async def delete_user(request):
    user = request.auth
    await user.adelete()
    return 200, {"message": "Account Deleted Successfully"}

#################################  F O R G O T  P A S S W O R D  #################################
@user_api.post("/forgot_password", auth=None, response={200: Message, 401: Message}, description="Send otp to user mobile to change password")
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

@user_api.post("/change_password", auth=None, response={200: Message, 400: Message, 401: Message, 403: Message}, description="Change password using OTP")
async def change_pwd(request, data: ResetPassword):
    key = f'change_pwd_{data.phone}'
    cache_value = await sync_to_async(cache.get)(key)
    if cache_value:
        if int(cache_value) == data.otp:
            user = await User.objects.aget(phone=data.phone)
            password = await sync_to_async(lambda: user.password)()
            if check_password(data.password, password):
                return 400, {"message": "New password can't be same as old password"}
            user.set_password(data.password)
            await user.asave()
            return 200, {"message": "Password changed successfully"}
        return 403, {"message": "Invalid OTP"}
    return 401, {"message": "OTP expired"}