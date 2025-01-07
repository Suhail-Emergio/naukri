from ninja import Router, PatchDict
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q
from asgiref.sync import sync_to_async

User = get_user_model()
details_api = Router(tags=['details'])

#################################  P E R S O N A L  D A T A  #################################
@details_api.post("/personal", response={201: PersonalData, 409: Message}, description="User personal data creation")
async def personal(request, data: PersonalCreation):
    if await Personal.objects.filter(user=request.auth).aexists():
        return 409, {"message": "Personal data already exists"}
    personal = await Personal.objects.acreate(**data.dict(), user=request.auth)
    return 201, personal

@details_api.patch("/personal", response={201: PersonalData, 404: Message, 409: Message}, description="User personal data update")
async def update_personal_data(request, data: PatchDict[PersonalCreation]):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        for attr, value in data.items():
            setattr(personal, attr, value)
        await personal.asave()
        return 201, personal
    return 404, {"message": "Personal data not found"}

@details_api.get("/personal", response={200: List[PersonalData], 409: Message}, description="User personal data")
async def personal_data(request):
    personal = [i async for i in Personal.objects.filter(user=request.auth)]
    return 200, personal

#################################  E M P L O Y M E N T  D A T A  #################################
@details_api.post("/employment", response={201: EmploymentData, 409: Message}, description="User employment data creation")
async def employment(request, data: EmploymentCreation):
    employment = await Employment.objects.acreate(**data.dict(), user=request.auth)
    return 201, employment

@details_api.patch("/employment", response={201: EmploymentData, 404: Message, 409: Message}, description="User employment data update")
async def update_employment_data(request, data: PatchDict[EmploymentData]):
    if await Employment.objects.filter(id=data['id']).aexists():
        employment = await Employment.objects.aget(id=data['id'])
        for attr, value in data.items():
            setattr(employment, attr, value)
        await employment.asave()
        return 201, employment
    return 404, {"message": "Employment data not found"}

@details_api.get("/employment", response={200: List[EmploymentData], 409: Message}, description="User employment data")
async def employment_data(request):
    employment = [i async for i in Employment.objects.filter(user=request.auth)]
    return 200, employment

#################################  Q U A L I F I C A T I O N  D A T A  #################################
@details_api.post("/qualification", response={201: QualificationData, 409: Message}, description="User Qualification data creation")
async def qualification(request, data: QualificationCreation):
    qualification = await Qualification.objects.acreate(**data.dict(), user=request.auth)
    return 201, qualification

@details_api.patch("/qualification", response={201: QualificationData, 404: Message, 409: Message}, description="User Qualification data update")
async def update_qualification_data(request, data: PatchDict[QualificationData]):
    if await Qualification.objects.filter(id=data['id']).aexists():
        qualification = await Qualification.objects.aget(id=data['id'])
        for attr, value in data.items():
            setattr(qualification, attr, value)
        await qualification.asave()
        return 201, qualification
    return 404, {"message": "Qualification data not found"}

@details_api.get("/qualification", response={200: List[QualificationData], 409: Message}, description="User Qualification data")
async def qualification_data(request):
    qualification = [i async for i in Qualification.objects.filter(user=request.auth)]
    return 200, qualification

#################################  P R E F E R E N C E  D A T A  #################################
@details_api.post("/preference", response={201: PreferenceData, 409: Message}, description="User preference data creation")
async def preference(request, data: PreferenceCreation):
    if await Preference.objects.filter(user=request.auth).aexists():
        return 409, {"message": "Preference data already exists"}
    preference = await Preference.objects.acreate(**data.dict(), user=request.auth)
    return 201, preference

@details_api.patch("/preference", response={201: PreferenceData, 404: Message, 409: Message}, description="User preference data update")
async def update_preference_data(request, data: PatchDict[PreferenceData]):
    if await Preference.objects.filter(user=request.auth).aexists():
        preference = await Preference.objects.aget(user=request.auth)
        for attr, value in data.items():
            setattr(preference, attr, value)
        await preference.asave()
        return 201, preference
    return 404, {"message": "Language data not found"}

@details_api.get("/preference", response={200: PreferenceData, 404: Message, 409: Message}, description="User preference data")
async def preference_data(request):
    if await Preference.objects.filter(user=request.auth).aexists():
        preference = await Preference.objects.aget(user=request.auth)
        return 200, preference
    return 404, {"message": "Preference data not found"}

#################################  L A N G U A G E S  #################################
@details_api.post("/add_language", response={201: Message, 404: Message, 409: Message}, description="User language data creation")
async def languages(request, data: LanguageData):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        language = await sync_to_async(lambda: personal.languages)() or {}
        count = len(language)
        language[count + 1] = data.dict()
        language[count + 1]['id'] = count + 1
        personal.languages = language
        await personal.asave()
        return 201, {"message": "Language added successfully"}
    return 404, {"message": "Personal data not found"}

@details_api.get("/languages", response={200: List[LanguageData], 404: Message, 409: Message}, description="User language data")
async def languages_data(request):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        language = await sync_to_async(lambda: personal.languages)()
        if language:
            languages_list = [LanguageData(**lang) for lang in language.values()]
            return 200, languages_list
        return 200, {}
    return 404, {"message": "Personal data not found"}

@details_api.patch("/update_language", response={201: Message, 404: Message, 403: Message, 409: Message}, description="User language data update")
async def update_languages_data(request, data: PatchDict[LanguageData], language_id:int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        language = await sync_to_async(lambda: personal.languages)()
        if language:
            if "id" not in data:
                language[language_id] = dict(data.items())
                language[language_id]['id'] = language_id
                personal.languages = language
                await personal.asave()
                return 201, {"message": "Language updated successfully"}
            return 403, {"message": "Id should not be passed in body"}
        return 409, {"message": "No language data found"}
    return 404, {"message": "Personal data not found"}

@details_api.delete("/delete_language", response={200: Message, 404: Message, 409: Message}, description="User language data deletion")
async def delete_languages_data(request, language_id: int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        language = await sync_to_async(lambda: personal.languages)()
        if language:
            del language[str(language_id)]
            personal.languages = language
            await personal.asave()
            return 200, {"message": "language removed successfully"}
        return 409, {"message": "No language data found"}
    return 404, {"message": "Personal data not found"}

@details_api.delete("/delete_all_languages", response={200: Message, 404: Message}, description="User languages data deletion")
async def delete_all_languages(request):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        personal.languages = {}
        await personal.asave()
        return 200, {"message": "All languages removed successfully"}
    return 404, {"message": "Personal data not found"}