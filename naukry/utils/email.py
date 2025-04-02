#################################  S E N D  E M A I L  #################################
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def send_mails(email, content, subject, html):
    username = email
    msg = EmailMultiAlternatives(subject, text, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html, "text/html")
    await sync_to_async(msg.send)()
    return {"status": True,"message" :"Email sended successfully"}

def send_interview_schedule(email, from_email, subject, body):
    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=[email],
    )
    msg.send()
    print("Email on scheduling interview sended successfully")

async def send_updates(email, subject, text_content, html_content):
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    await sync_to_async(msg.send)()
    print("Email sended successfully")