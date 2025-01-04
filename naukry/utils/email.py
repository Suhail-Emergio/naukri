#################################  S E N D  E M A I L  #################################
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def send_mails(email, name, password):
    username = email
    temporary_password = password
    subject = "Naukri Login Credentials"
    text_content = f"""
        Dear {name},

        This is an important message regarding your Naukri account.
        Your login credentials have been updated. Please find the details below:

        Username: {username}
        Temporary Password: {temporary_password}

        For security reasons, we recommend changing your password upon your first login.
        If you didn't request this change, please contact our support team immediately.

        Naukri Team
    """

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Naukri Login Credentials</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .header {{
                        background-color: #4CAF50;
                        color: white;
                        text-align: center;
                        padding: 20px;
                        font-size: 24px;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #fff;
                        border: 1px solid #ddd;
                        border-radius: 0 0 5px 5px;
                        padding: 20px;
                        margin-top: -1px;
                    }}
                    .important {{
                        color: #ff4500;
                        font-weight: bold;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #777;
                    }}
                    ul {{
                        list-style-type: none;
                        padding: 0;
                    }}
                    ul li {{
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
            <div class="header">
                Naukri Login Credentials
            </div>
            <div class="content">
                <p>Dear {name},</p>
                <p>This is an <span class="important">important</span> message regarding your Naukri account.</p>
                <p>Your login credentials have been updated. Please find the details below:</p>
                <ul>
                    <li><strong>Username:</strong> {username}</li>
                    <li><strong>Temporary Password:</strong> {temporary_password}</li>
                </ul>
                <p>For security reasons, we recommend changing your password upon your first login.</p>
                <p>If you didn't request this change, please contact our support team immediately.</p>
            </div>
            <div class="footer">
                &copy; 2024 Naukri. All rights reserved.
            </div>
            </body>
        </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    await sync_to_async(msg.send)()
    return {"status": True,"message" :"Email sended successfully"}

async def send_interview_schedule(email, subject, body):
    msg = EmailMultiAlternatives(subject, body, settings.EMAIL_HOST_USER, [email])
    await sync_to_async(msg.send)()
    return {"status": True,"message" :"Email sended successfully"}