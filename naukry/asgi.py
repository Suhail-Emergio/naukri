# import os
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naukry.settings')


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'naukry.settings')

import django
django.setup()

from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from web_sockets.main import app as websocket_app


application = get_asgi_application()
app = FastAPI()

app.mount("/django", WSGIMiddleware(application))
app.mount("/ws", websocket_app)