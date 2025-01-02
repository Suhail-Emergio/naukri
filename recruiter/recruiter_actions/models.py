from django.db import models
from django.contrib.auth import get_user_model
from seeker.details.models import Personal

User = get_user_model()

class SaveCandidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Personal, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)