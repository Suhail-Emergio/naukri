from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from seeker.details.models import NotificationPreference

@receiver(post_save, sender=UserProfile)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        NotificationPreference.objects.create(user=instance)