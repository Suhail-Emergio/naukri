from ninja import Schema
from typing import *

class UserData(Schema):
    id: int
    username: str

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
    username: str
    whatsapp_updations: bool

class TokenSchema(Schema):
    access: str
    refresh: str

class TokenRefreshSchema(Schema):
    refresh: str