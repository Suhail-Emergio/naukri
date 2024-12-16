from ninja.security import HttpBearer
from user.models import *
import jwt
from django.conf import settings

class AsyncJWTAuth(HttpBearer):
    async def authenticate(self, request, token):
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        user = await UserProfile.objects.aget(id=user_id)
        return user