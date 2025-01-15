# # import os
# # from django.core.asgi import get_asgi_application

# # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naukry.settings')


# import os
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naukry.settings')

# import django
# django.setup()

# from django.core.asgi import get_asgi_application
# from fastapi import FastAPI
# from fastapi.middleware.wsgi import WSGIMiddleware
# from web_sockets.main import app as api_router
# from django.conf import settings

# application = get_asgi_application()
# app = FastAPI()

# app = FastAPI()
# app.add_middleware(
#     WSGIMiddleware,
#     allow_origins=settings.ALLOWED_HOSTS or ["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# app.include_router(api_router, prefix="/api")
# app.mount("/django", WSGIMiddleware(application))

# naukry/asgi.py
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