from django.contrib.auth import get_user_model
from recruiter.recruiter_actions.models import ApplyJobs
from recruiter.recruiter_actions.utils.random_pass import random_password_generation

User = get_user_model()

async def candidate_creation(email, job):
    candidates = []
    if await User.objects.filter(email=email).aexists():
        user = await User.objects.aget(email=email)
        candidates.append(user)
    else:
        password = random_password_generation()
        user = await User.objects.acreate(email=email, username=email)
        user.set_password(password)
        await user.asave()
        candidates.append(user)
    for candidate in candidates:
        if not await ApplyJobs.objects.filter(user=candidate, job=job).aexists():
            await ApplyJobs.objects.acreate(user=candidate, job=job, status="applied")