from django.core.management.base import BaseCommand
from common_actions.models import Subscription
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from django.db.models import F, ExpressionWrapper, DateField

class Command(BaseCommand):
    help = 'Notify user of expiry of plan and on expiry date delete plans'

    def handle(self, *args, **options):
        today = timezone.now().date()
        is_weekend = today.weekday() in (5)
        subscriptions = Subscription.objects.annotate(expiry_date=ExpressionWrapper(F('subscribed_on') + F('plan__duration'),output_field=DateField())).filter(expiry_date=today)
        subscriptions.delete()
        if is_weekend:
            subject="Your Plans validity is gonna expire soon. Contact admin for increasing validity"
            for i in Subscription.objects.annotate(expiry_date=ExpressionWrapper(F('subscribed_on') + F('plan__duration'),output_field=DateField())).filter(expiry_date__lte=today):
                send_notifications(onesignal_id=i.user.onesignal_id, subject=subject, title="Plans updations")
                send_updates(body=subject, number=i.user.phone)