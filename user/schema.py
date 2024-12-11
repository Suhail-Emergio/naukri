from ninja import Schema
from typing import *

class UserData(Schema):
    id: int
    username: str

class Message(Schema):
    message: str

class MobileLogin(Schema):
    password: str
    username: str

class EmailLogin(Schema):
    password: str
    email: str

class UserCreation(Schema):
    name: str
    password: str
    email: str
    phone: str
    username: str

class TokenSchema(Schema):
    access: str
    refresh: str

class TokenRefreshSchema(Schema):
    refresh: str