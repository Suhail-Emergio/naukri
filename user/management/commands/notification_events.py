from django.core.management.base import BaseCommand
from naukry.utils.twilio import send_updates
from naukry.utils.notification import send_notifications
from django.contrib.auth import get_user_model
from naukry.utils.profile_completion import completion_data
from asgiref.sync import sync_to_async, async_to_sync
from jobs.job_actions.models import SaveJobs
from common_actions.models import Suggestions
from jobs.jobposts.models import JobPosts
from seeker.details.models import Personal, Preference
from django.db.models import Q
from common_actions.models import Notification
from django.utils.timezone import now
from django.utils import timezone
from seeker.details.models import SearchApps
from seeker.details.models import NotificationPreference as Np
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from naukry.utils.email import send_updates
from recruiter.company.models import CompanyDetails

User = get_user_model()

class Command(BaseCommand):
    help = 'Notify user of updations'

    def handle(self, *args, **options):
        today = timezone.now().date()
        self.search_apps_creation()
        for j in Np.objects.all():
            noti_day = today.weekday() == 6 if j.alerts == "weekly" else True if j.alerts == "daily" else None
            if noti_day:
                self.post_completion(j.user)
                self.saved_jobs(today, j.user)
                self.feedback_request(today, j.user)
        # self.inactive_users()
            rec_day = today.weekday() == 7 if j.recommendations == "weekly" else True if j.alerts == "daily" else None
            if rec_day:
                self.recommendations()

    def search_apps_creation(self):
        for i in User.objects.filter(role="seeker"):
            SearchApps.objects.create(user=i)
            print(f"search apps for {i} is created")

    def post_completion(self, user):
        profile_completion_percentage, empty_models, models_with_empty_fields = sync_to_async(completion_data)(user)
        if profile_completion_percentage < 100:
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="Complete your profile for better visibility to recruiters.", title="Profile completion")
            notification = Notification.objects.create(
                title="Profile completion",
                description="Complete your profile for better visibility to recruiters.",
                created_on=now()
            )
            notification.user.add(i)

    def saved_jobs(self, today, user):
        if SaveJobs.objects.filter(job__expire_on__lt=today, user=user):
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="Your saved jobs gonna expire soon. Take action before late.", title="Saved jobs updations")
            notification = Notification.objects.create(
                title="Saved jobs updations",
                description="Your saved jobs gonna expire soon. Take action before late.",
                created_on=now()
            )
            notification.user.add(user)

    def feedback_request(self, today, user):
        if not Suggestions.objects.filter(user=user).exists():
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="Give us your feedback & suggestions", title="Feedback & Suggestions")
            notification = Notification.objects.create(
                title="Feedback & Suggestions",
                description="Give us your feedback & suggestions",
                created_on=now()
            )
            notification.user.add(user)

    # def inactive_users(self, today):
    #     pass

    def recommendations(self):
        for i in User.objects.filter():
            if i.role == "seeker":
                if Preference.objects.filter(user=i).exists():
                    preference = Preference.objects.get(user=i)
                    posts = JobPosts.objects.filter(
                        Q(type__in=preferences.job_type) |
                        Q(city__in=preferences.job_location) |
                        Q(type__in=preferences.employment_type) |
                        Q(type__in=preferences.employment_type) |
                        Q(title__icontains=preferences.job_role)
                    )[:10]
                else:
                    posts = JobPosts.objects.all()[:10]
            else:
                company = CompanyDetails.objects.get(user=i)
                posts = Personal.objects.filter(skills__in=company.functional_area)[:10]
            context = {
                'posts': posts,
                'job_detail_url': 'https://yourdomain.com/jobs/',
                'unsubscribe_url': 'https://yourdomain.com/unsubscribe/'
            }
            html_message = render_to_string('templates\recommended.html', context)
            plain_message = strip_tags(html_message)
            send_updates(email=i.email, html_content=plain_message, text_content="Job Recommendations", subject="Job Recommendations")

    def send_noti(self, onesignal_id, whatsapp_updations, phone, subject, title):
        if onesignal_id:
            send_notifications(onesignal_id=onesignal_id, subject=subject, title=title)
        if whatsapp_updations:
            send_updates(body=subject, number=phone)