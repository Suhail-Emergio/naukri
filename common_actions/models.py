from django.db import models
from django.contrib.auth import get_user_model
from recruiter.company.models import CompanyDetails as Company
from administrator.admin_actions.models import Plans, Banner

User = get_user_model()

class Suggestions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    remaining_posts = models.IntegerField(default=0)
    transaction_id = models.CharField(max_length=100)
    subscribed_on = models.DateField(auto_now=True)

class Notification(models.Model):
    user = models.ManyToManyField(User, related_name='notifications', blank=True)
    title =  models.CharField(max_length=100)
    description = models.TextField()
    image = models.FileField(upload_to='notification/image', null=True, blank=True)
    url = models.URLField(max_length=200,null=True,blank=True)
    created_on = models.DateTimeField(auto_now=True)
    read_by = models.ManyToManyField(User, related_name='read_notifications', blank=True)