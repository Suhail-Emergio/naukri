from django.core.management.base import BaseCommand
from common_actions.models import Subscription
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from django.db.models import F, ExpressionWrapper, DateField
from seeker.details.models import NotificationPreference

class Command(BaseCommand):
    help = 'Notify user of expiry of plan and on expiry date delete plans'

    def handle(self, *args, **options):
        today = timezone.now().date()
        subscriptions = Subscription.objects.annotate(
            expiry_date=ExpressionWrapper(F('subscribed_on') + F('plan__duration'),output_field=DateField())
        ).filter(expiry_date=today)
        subscriptions.delete()
        for j in NotificationPreference.objects.all():
            noti_day = today.weekday() == 5 if j.alerts == "weekly" else True if j.alerts == "daily" else None
            if noti_day:
                subject="Your Plans validity is gonna expire soon. Contact admin for increasing validity"
                subscription = Subscription.objects.annotate(expiry_date=ExpressionWrapper(F('subscribed_on') + F('plan__duration'),output_field=DateField())).filter(expiry_date__lte=today, user=j.user).exists()
                if subscription:
                    if j.mobile_notifications and j.user.onesignal_id:
                        send_notifications(onesignal_id=j.user.onesignal_id, subject=subject, title="Plans updations")
                    if j.user.whatsapp_updations:
                        send_updates(body=subject, number=j.user.phone)