from ninja import Router, PatchDict, UploadedFile, File
from django.contrib.auth import get_user_model
from .schema import *
from typing import *
from .models import *
from user.schema import *
from django.db.models import Q
from asgiref.sync import sync_to_async
from jobs.job_actions.models import ApplyJobs
from naukry.utils.profile_completion import completion_data

User = get_user_model()
details_api = Router(tags=['details'])

#################################  P E R S O N A L  D A T A  #################################
@details_api.post("/personal", response={201: Message, 409: Message}, description="User personal data creation")
async def personal(request, data: PersonalCreation, cv: Optional[UploadedFile] = None, profile_image: Optional[UploadedFile] = None):
    if await Personal.objects.filter(user=request.auth).aexists():
        return 409, {"message": "Personal data already exists"}
    personal = await Personal.objects.acreate(**data.dict(), user=request.auth)
    if cv:
        await sync_to_async(personal.cv.save)(cv.name, cv)
    if profile_image:
        await sync_to_async(personal.profile_image.save)(profile_image.name, profile_image)
    return 201, {"message": "Personal data created"}

@details_api.patch("/personal", response={201: Message, 404: Message, 409: Message}, description="User personal data update")
async def update_personal_data(request, data: PatchDict[PersonalCreation]):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        for attr, value in data.items():
            setattr(personal, attr, value)
        await personal.asave()
        return 201, {"message": "Succesfully updated"}
    return 404, {"message": "Personal data not found"}

@details_api.get("/personal", response={200: PersonalSchema, 404: Message, 409: Message}, description="User personal data")
async def personal_data(request):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        return 200, {"personal": personal, "user": request.auth}
    return 404, {"message": "Personal data not found"}

@details_api.post("/personal/cv", response={201: Message, 404: Message}, description="Upload or update user CV")
async def update_cv(request, cv: UploadedFile = File(...)):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        personal.cv = cv
        await personal.asave()
        return 201, {"message": "CV updated successfully"}
    return 404, {"message": "Personal data not found"}

@details_api.post("/personal/profile_image", response={201: Message, 404: Message}, description="Upload or update user image")
async def update_profile_image(request, profile_image: UploadedFile = File(...)):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        personal.profile_image = profile_image
        await personal.asave()
        return 201, {"message": "Image updated successfully"}
    return 404, {"message": "Personal data not found"}

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

@details_api.delete("/delete_employment", response={200: Message, 404: Message, 409: Message}, description="User employment data deletion")
async def delete_employment(request, id: int):
    if await Employment.objects.filter(id=id).aexists():
        employment = await Employment.objects.aget(id=id)
        await employment.adelete()
        return 200, {"message": "Employment data deleted successfully"}
    return 409, {"message": "Employment data not found"}

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

@details_api.delete("/delete_qualification", response={200: Message, 404: Message, 409: Message}, description="User qualification data deletion")
async def delete_qualification(request, id: int):
    if await Qualification.objects.filter(id=id).aexists():
        qualification = await Qualification.objects.aget(id=id)
        await qualification.adelete()
        return 200, {"message": "Qualification data deleted successfully"}
    return 404, {"message": "Qualification data not found"}

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
        return 200, []
    return 404, {"message": "Personal data not found"}

@details_api.patch("/update_language", response={201: Message, 404: Message, 403: Message, 409: Message}, description="User language data update")
async def update_languages_data(request, data: PatchDict[LanguageData]):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        language = await sync_to_async(lambda: personal.languages)()
        if language:
            language[data.get("id")] = dict(data.items())
            personal.languages = language
            await personal.asave()
            return 201, {"message": "Language updated successfully"}
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

#################################  C E R T I F I C A T E S  #################################
@details_api.post("/add_certificates", response={201: Message, 404: Message, 409: Message}, description="User certificate data creation")
async def certificates(request, data: CertificateData):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        certificate = await sync_to_async(lambda: personal.certificates)() or {}
        count = len(certificate)
        certificate[count + 1] = data.dict()
        certificate[count + 1]['id'] = count + 1
        personal.certificates = certificate
        await personal.asave()
        return 201, {"message": "certificate added successfully"}
    return 404, {"message": "Personal data not found"}

@details_api.get("/certificates", response={200: List[CertificateData], 404: Message, 409: Message}, description="User certificate data")
async def certificates_data(request):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        certificate = await sync_to_async(lambda: personal.certificates)()
        if certificate:
            certificates_list = [CertificateData(**lang) for lang in certificate.values()]
            return 200, certificates_list
        return 200, []
    return 404, {"message": "Personal data not found"}

@details_api.patch("/update_certificate", response={201: Message, 404: Message, 403: Message, 409: Message}, description="User certificate data update")
async def update_certificates_data(request, data: PatchDict[CertificateData], certificate_id:int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        certificate = await sync_to_async(lambda: personal.certificates)()
        if certificate:
            if "id" not in data:
                certificate[certificate_id] = dict(data.items())
                certificate[certificate_id]['id'] = certificate_id
                personal.certificates = certificate
                await personal.asave()
                return 201, {"message": "certificate updated successfully"}
            return 403, {"message": "Id should not be passed in body"}
        return 409, {"message": "No certificate data found"}
    return 404, {"message": "Personal data not found"}

@details_api.delete("/delete_certificate", response={200: Message, 404: Message, 409: Message}, description="User certificate data deletion")
async def delete_certificates_data(request, certificate_id: int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        certificate = await sync_to_async(lambda: personal.certificates)()
        if certificate:
            del certificate[str(certificate_id)]
            personal.certificates = certificate
            await personal.asave()
            return 200, {"message": "certificate removed successfully"}
        return 409, {"message": "No certificate data found"}
    return 404, {"message": "Personal data not found"}

#################################  P R O J E C T S  #################################
@details_api.post("/add_project", response={201: Message, 404: Message, 409: Message}, description="User project data creation")
async def projects(request, data: ProjectData):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        project = await sync_to_async(lambda: personal.projects)() or {}
        count = len(project)
        project[count + 1] = data.dict()
        project[count + 1]['id'] = count + 1
        personal.projects = project
        await personal.asave()
        return 201, {"message": "project added successfully"}
    return 404, {"message": "Personal data not found"}

@details_api.get("/projects", response={200: List[ProjectData], 404: Message, 409: Message}, description="User project data")
async def projects_data(request):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        project = await sync_to_async(lambda: personal.projects)()
        if project:
            projects_list = [ProjectData(**lang) for lang in project.values()]
            return 200, projects_list
        return 200, []
    return 404, {"message": "Personal data not found"}

@details_api.patch("/update_project", response={201: Message, 404: Message, 403: Message, 409: Message}, description="User project data update")
async def update_projects_data(request, data: PatchDict[ProjectData], project_id:int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        project = await sync_to_async(lambda: personal.projects)()
        if project:
            if "id" not in data:
                project[project_id] = dict(data.items())
                project[project_id]['id'] = project_id
                personal.projects = project
                await personal.asave()
                return 201, {"message": "project updated successfully"}
            return 403, {"message": "Id should not be passed in body"}
        return 409, {"message": "No project data found"}
    return 404, {"message": "Personal data not found"}

@details_api.delete("/delete_project", response={200: Message, 404: Message, 409: Message}, description="User project data deletion")
async def delete_projects_data(request, project_id: int):
    if await Personal.objects.filter(user=request.auth).aexists():
        personal = await Personal.objects.aget(user=request.auth)
        project = await sync_to_async(lambda: personal.projects)()
        if project:
            del project[str(project_id)]
            personal.projects = project
            await personal.asave()
            return 200, {"message": "project removed successfully"}
        return 409, {"message": "No project data found"}
    return 404, {"message": "Personal data not found"}

#################################  C O U N T S  #################################
@details_api.get("/user_counts", response={200: CountData, 404: Message, 409: Message}, description="showing perc of profile completion, Count of jobs applied, Count of jobs viewed by recruiers, Count of interviews scheduled by recruiers, remaining datas to enter in profile ")
async def counts(request):
    profile_completion_percentage, empty_models, models_with_empty_fields = await completion_data(request.auth)
    applied_jobs_count = await ApplyJobs.objects.filter(user=request.auth).acount()
    jobs_viewed_count = await ApplyJobs.objects.filter(user=request.auth, viewed=False).acount()
    interview_scheduled_count = await ApplyJobs.objects.filter(user=request.auth, status="shortlisted").acount()
    return 200, {
        "profile_completion_percentage": profile_completion_percentage,
        "empty_models": empty_models,
        "models_with_empty_fields": models_with_empty_fields,
        "applied_jobs_count": applied_jobs_count,
        "jobs_viewed_count": jobs_viewed_count,
        "interview_scheduled_count": interview_scheduled_count
    }

#################################   N O T I F I C A T  I O N  P R E F E R E N C E  #################################
@details_api.patch("/update_notification_preference", response={201: Message, 404: Message, 409: Message}, description="User preference data update")
async def update_notification_preference(request, data: PatchDict[NotificationPreferencePatch]):
    if await Preference.objects.filter(user=request.auth).aexists():
        preference = await NotificationPreference.objects.aget(user=request.auth)
        for attr, value in data.items():
            setattr(preference, attr, value)
        await preference.asave()
        return 201, {"message": "Successfully updated"}
    return 404, {"message": "Preference data not found"}

@details_api.get("/notification_preference", response={200: NotifactionPreferenceData, 404: Message, 409: Message}, description="User preference data")
async def notification_preference(request):
    if await NotificationPreference.objects.filter(user=request.auth).aexists():
        preference = await NotificationPreference.objects.aget(user=request.auth)
        return 200, preference
    return 404, {"message": "Preference data not found"}