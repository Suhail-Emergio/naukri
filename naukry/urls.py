from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from .utils.auth import *
from user.views import *
from seeker.details.views import *

api = NinjaAPI(auth=AsyncJWTAuth())
api.add_router('user', user_api)
api.add_router('personal', personal_api)
api.add_router('employment', employment_api)
api.add_router('professional', professional_api)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)