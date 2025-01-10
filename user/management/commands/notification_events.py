from django.core.management.base import BaseCommand
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from django.contrib.auth import get_user_model
from naukry.utils.profile_completion import completion_data
from asgiref.sync import sync_to_async
from jobs.job_actions.models import SaveJobs
from common_actions.models import Suggestions
from jobs.jobposts.models import JobPosts
from seeker.details.models import Personal, Preference
from django.db.models import Q
from common_actions.models import Notification
from django.utils.timezone import now

User = get_user_model()

class Command(BaseCommand):
    help = 'Notify user of updations'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.post_completion(today)
        self.saved_jobs(today)
        self.feedback_request(today)
        # self.inactive_users()
        # self.recommendations()

    def post_completion(self, today):
        noti_day = today.weekday() in (6)
        if noti_day:
            for i in User.objects.filter(role="seeker"):
                profile_completion_percentage, empty_models, models_with_empty_fields = await sync_to_async(completion_data(i))
                if profile_completion_percentage < 100:
                    self.send_noti(onesignal_id=i.onesignal_id, whatsapp_updations=i.whatsapp_updations, phone=i.phone, subject="Complete your profile for better visibility to recruiters.", title="Profile completion")
                    notification = Notification.objects.create(
                        title="Profile completion",
                        description="Complete your profile for better visibility to recruiters.",
                        created_on=now()
                    )
                    notification.user.add(i)

    def saved_jobs(self, today):
        noti_day = today.weekday() in (3)
        if noti_day:
            for i in SaveJobs.objects.filter(job__expire_on__lt=today):
                self.send_noti(onesignal_id=i.user.onesignal_id, whatsapp_updations=i.user.whatsapp_updations, phone=i.user.phone, subject="Your saved jobs gonna expire soon. Take action before late.", title="Saved jobs updations")
                notification = Notification.objects.create(
                    title="Saved jobs updations",
                    description="Your saved jobs gonna expire soon. Take action before late.",
                    created_on=now()
                )
                notification.user.add(i.user)

    def feedback_request(self, today):
        month_start = today.replace(day=1)
        for i in User.objects.all():
            if not Suggestions.objects.filter(user=i).exists():
                self.send_noti(onesignal_id=i.user.onesignal_id, whatsapp_updations=i.user.whatsapp_updations, phone=i.user.phone, subject="Give us your feedback & suggestions", title="Feedback & Suggestions")
                notification = Notification.objects.create(
                    title="Feedback & Suggestions",
                    description="Give us your feedback & suggestions",
                    created_on=now()
                )
                notification.user.add(i)

    # def inactive_users(self, today):
    #     pass

    # def recommendations(self):
    #     for i in User.objects.filter():
    #         if Preference.objects.filter(user=i).exists():
    #             preference = Preference.objects.get(user=i)
    #             if i.role == "seeker":
    #                 jobs = JobPosts.objects.filter(
    #                     Q(type__in=preferences.job_type) |
    #                     Q(city__in=preferences.job_location) |
    #                     Q(type__in=preferences.employment_type) |
    #                     Q(type__in=preferences.employment_type) |
    #                     Q(title__icontains=preferences.job_role)
    #                 )[:10]


    def send_noti(self, onesignal_id, whatsapp_updations, phone, subject, title):
        if onesignal_id:
            send_notifications(onesignal_id=onesignal_id, subject=subject, title=title)
        if whatsapp_updations:
            send_updates(body=subject, number=phone)