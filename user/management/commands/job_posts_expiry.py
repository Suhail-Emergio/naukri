from django.core.management.base import BaseCommand
from jobs.jobposts.models import JobPosts
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from seeker.details.models import NotificationPreference
from jobs.job_actions.models import SaveJobs

class Command(BaseCommand):
    help = 'Notify user of expiry of job posts and on expiry date delete job posts'

    def handle(self, *args, **options):
        today = timezone.now().date()
        for j in NotificationPreference.objects.all():
            noti_day = today.weekday() == 5 if j.alerts == "weekly" else True if j.alerts == "daily" else None
            if noti_day:
                subject="Your job posts validity is gonna expire soon. Contact admin for increasing validity."
                if JobPosts.objects.filter(expire_on__lte=today, company__user=j.user).exists():
                    if j.user.onesignal_id and j.mobile_notifications:
                        send_notifications(onesignal_id=j.user.onesignal_id, subject=subject, title="Job posts updations")
                    if j.user.whatsapp_updations:
                        send_updates(body=subject, number=j.user.phone)