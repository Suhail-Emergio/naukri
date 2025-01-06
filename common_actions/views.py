from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .schema import *
from typing import *
from .models import *
from user.schema import *

User = get_user_model()
common_api = Router(tags=['common'])

#################################  S U G G E S T I O N S  #################################
@common_api.post("/suggestion", response={201: Message, 409:Message}, description="Suggestion creations")
async def suggestions(request, data: SuggestionCreation):
    user = request.auth
    suggestion = await Suggestions.objects.acreate(**data.dict())
    await suggestion.asave()
    return 201, {"message" : "Suggestion created successfuly"}