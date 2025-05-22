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
from naukry.utils.twilio import send_updates
from naukry.utils.email import send_updates as email_send
from recruiter.company.models import CompanyDetails

User = get_user_model()

class Command(BaseCommand):
    help = 'Notify user of updations'

    def handle(self, *args, **options):
        today = timezone.now().date()
        send_updates(body="expiry of job posts", number="8075697608")
        for j in Np.objects.all():
            noti_day = today.weekday() == 6 if j.alerts == "weekly" else True if j.alerts == "daily" else None
            if noti_day:
                self.post_completion(j.user)
                self.saved_jobs(today, j.user)
                self.feedback_request(today, j.user)
            rec_day = today.weekday() == 7 if j.recommendations == "weekly" else True if j.alerts == "daily" else None
            if rec_day:
                self.recommendations()

    def post_completion(self, user):
        profile_completion_percentage, empty_models, models_with_empty_fields = async_to_sync(completion_data)(user)
        if profile_completion_percentage < 100:
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="Increase your chances of getting noticed by recruiters! Complete your profile with all relevant details to enhance your visibility and stand out to potential employers. Don’t miss out on exciting opportunities — update your profile today!", title="Profile completion")
            notification = Notification.objects.create(
                title="Profile completion",
                description="Increase your chances of getting noticed by recruiters! Complete your profile with all relevant details to enhance your visibility and stand out to potential employers. Don’t miss out on exciting opportunities — update your profile today!",
                created_on=now()
            )
            notification.user.add(i)

    def saved_jobs(self, today, user):
        if SaveJobs.objects.filter(job__end_date__lt=today, user=user):
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="Heads up! The jobs you’ve saved are nearing their expiration. Don’t miss out on these opportunities — take action now to apply or update your selections before they’re gone. Secure your next career move today!", title="Saved jobs updations")
            notification = Notification.objects.create(
                title="Saved jobs updations",
                description="Heads up! The jobs you’ve saved are nearing their expiration. Don’t miss out on these opportunities — take action now to apply or update your selections before they’re gone. Secure your next career move today!",
                created_on=now()
            )
            notification.user.add(user)

    def feedback_request(self, today, user):
        if not Suggestions.objects.filter(user=user).exists():
            self.send_noti(onesignal_id=user.onesignal_id, whatsapp_updations=user.whatsapp_updations, phone=user.phone, subject="We value your thoughts! Share your feedback and suggestions to help us improve your experience. Your input plays a crucial role in shaping our services — let your voice be heard!", title="Feedback & Suggestions")
            notification = Notification.objects.create(
                title="Feedback & Suggestions",
                description="We value your thoughts! Share your feedback and suggestions to help us improve your experience. Your input plays a crucial role in shaping our services — let your voice be heard!",
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
                        Q(type__in=preference.job_type) |
                        Q(city__in=preference.job_location) |
                        Q(type__in=preference.employment_type) |
                        Q(type__in=preference.employment_type) |
                        Q(title__icontains=preference.job_role)
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
            html_message = render_to_string('recommended.html', context)
            plain_message = strip_tags(html_message)
            async_to_sync(email_send)(email=i.email, html_content=plain_message, text_content="Job Recommendations", subject="Job Recommendations")

    def send_noti(self, onesignal_id, whatsapp_updations, phone, subject, title):
        if onesignal_id:
            send_notifications(onesignal_id=onesignal_id, subject=subject, title=title)
        if whatsapp_updations:
            send_updates(body=subject, number=phone)