from ninja import Schema
from typing import *
from ninja import ModelSchema
from django.contrib.auth import get_user_model

User = get_user_model()

class UserData(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'role', 'email']

class Message(Schema):
    message: str

class LoginSchema(Schema):
    username: str
    password: str | None = None
    role: str

class MobileOtpVerify(Schema):
    phone: str
    email: str | None = None

class EmailOtp(Schema):
    email: str

class EmailOtpVerify(Schema):
    email: str
    otp: int | None = None

class ForgotPassword(Schema):
    phone : str

class ResetPassword(Schema):
    phone : str
    otp : int
    password: str

class UserCreation(Schema):
    name: str | None = None
    password: str | None = None
    email: str | None = None
    phone: str
    role: str | None = None
    otp: int
    onesignal_id: str | None = None
    whatsapp_updations: bool | None = None

class SocialSignupSchema(Schema):
    email: str  # Required for identifying the user
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    onesignal_id: Optional[str] = None
    whatsapp_updations: Optional[bool] = None

class TokenSchema(Schema):
    access: str
    refresh: str
    name:Optional[str]
    role: Optional[str]

class TokenRefreshSchema(Schema):
    refresh: str