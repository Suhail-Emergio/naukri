from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10, unique=True)
    total_hr_spend = models.FloatField(default=0.0)
    active_from = models.DateTimeField(null=True, blank=True)
    inactive_from = models.DateTimeField(null=True, blank=True)
    deactivate = models.BooleanField(default=False)
    deactivated_on = models.DateField(null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='userprofile_set',  # Custom related_name
        help_text='The groups this user belongs to.'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='userprofile_set',  # Custom related_name
        help_text='Specific permissions for this user.'
    )