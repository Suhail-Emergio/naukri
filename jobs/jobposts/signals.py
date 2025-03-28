from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.utils import timezone
from common_actions.models import Subscription

@receiver(post_save, sender=JobPosts)
def log_model_save(sender, instance, created, **kwargs):
    if created:
        user = instance.company.user
        if Subscription.objects.filter(user = user).exists():
            subscribe = Subscription.objects.get(user = user)

            if subscribe.remaining_posts != 0:
                subscribe.remaining_posts -= 1
            if subscribe.remaining_posts == 0:
                user.subcribed = False
                user.save()
                subscribe.delete()

            subscribe.save()