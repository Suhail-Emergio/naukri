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