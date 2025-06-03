import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naukry.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from django.conf import settings
from web_sockets.main import router

fastapi_app = FastAPI()

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fastapi_app.include_router(router)

django_application = get_asgi_application()

async def application(scope, receive, send):
    if scope["type"] == "websocket":
        await fastapi_app(scope, receive, send)
    else:
        await django_application(scope, receive, send)
# async def application(scope, receive, send):
#     if scope["type"] == "websocket" and scope["path"].startswith("/ws"):
#         await fastapi_app(scope, receive, send)
#     else:
#         await django_application(scope, receive, send)
