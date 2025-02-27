from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from seeker.details.models import SearchApps
from administrator.admin_actions.models import Banner
from jobs.jobposts.models import JobPosts
from jobs.job_actions.models import SaveJobs
from common_actions.models import Subscription
from django.db.models import F, ExpressionWrapper, DateField

User = get_user_model()

class Command(BaseCommand):
    help = 'Notify user of updations'

    def handle(self, *args, **options):
        self.today = timezone.now().date()
        self.search_apps_creation()
        self.banner_deletion()
        self.job_deletion()

    def search_apps_creation(self):
        for i in User.objects.filter(role="seeker", is_superuser=False):
            if SearchApps.objects.filter(user=i, date=self.today).exists():
                SearchApps.objects.filter(user=i, date=self.today).delete()
            SearchApps.objects.create(user=i)
            print(f"search apps for {i} is created")

    def banner_deletion(self):
        banners = Banner.objects.annotate(
            expiry_date=ExpressionWrapper(F('created_on') + F('duration'), output_field=DateField())
        ).filter(expiry_date=self.today)
        banners.delete()

    def subscription_deletion(self):
        subscriptions = Subscription.objects.annotate(
            expiry_date=ExpressionWrapper(F('subscribed_on') + F('plan__duration'),output_field=DateField())
        ).filter(expiry_date=self.today)
        subscriptions.delete()

    def job_deletion(self):
        JobPosts.objects.filter(expire_on=self.today).update(active=False)
        SaveJobs.objects.filter(job__expire_on=self.today).delete()