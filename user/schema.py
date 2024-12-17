from ninja import Schema
from typing import *

class UserData(Schema):
    id: int
    username: str
    role: str

class Message(Schema):
    message: str

class MobileLogin(Schema):
    username: str
    password: str

class EmailLogin(Schema):
    email: str
    password: str | None = None

class UserCreation(Schema):
    name: str
    password: str
    email: str
    phone: str
    role: str
    whatsapp_updations: bool

class TokenSchema(Schema):
    access: str
    refresh: str

class TokenRefreshSchema(Schema):
    refresh: str