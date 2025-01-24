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

class MobileOtpVerify(Schema):
    phone: str
    otp: str

class EmailOtpVerify(Schema):
    email: str
    otp: int | None = None

class ForgotPassword(Schema):
    phone : str

class ResetPassword(Schema):
    phone : str
    password: str

class UserCreation(Schema):
    name: str
    password: str
    email: str
    phone: str
    role: str
    onesignal_id: str
    whatsapp_updations: bool

class TokenSchema(Schema):
    access: str
    refresh: str
    name:Optional[str]
    role: Optional[str]

class TokenRefreshSchema(Schema):
    refresh: str