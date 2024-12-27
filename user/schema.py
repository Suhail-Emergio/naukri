from ninja import Schema
from typing import *

class UserData(Schema):
    username: str
    role: str

class Message(Schema):
    message: str

class LoginSchema(Schema):
    username: str
    password: str

class MobileOtpVerify(Schema):
    phone: str
    otp: str

class EmailOtpVerify(Schema):
    otp: int

class ForgotPassword(Schema):
    phone : str

class ResetPassword(Schema):
    phone : str | None = None
    otp : int | None = None
    password: str

class UserCreation(Schema):
    name: str
    password: str
    email: str
    phone: str
    username: str | None = None
    role: str
    whatsapp_updations: bool

class TokenSchema(Schema):
    access: str
    refresh: str

class TokenRefreshSchema(Schema):
    refresh: str