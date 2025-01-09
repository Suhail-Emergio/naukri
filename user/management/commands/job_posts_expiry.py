from django.core.management.base import BaseCommand
from jobs.jobposts.models import JobPosts
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications

class Command(BaseCommand):
    help = 'Notify user of expiry of job posts and on expiry date delete job posts'

    def handle(self, *args, **options):
        today = timezone.now().date()
        is_weekend = today.weekday() in (5)
        JobPosts.objects.filter(expire_on=today).delete()
        if is_weekend:
            subject="Your job posts validity is gonna expire soon. Contact admin for increasing validity"
            for i in JobPosts.objects.filter(expire_on__lte=today):
                send_notifications(onesignal_id=i.company.user.onesignal_id, subject=subject, title="Job posts updations")
                send_updates(body=subject, number=i.company.user.phone)