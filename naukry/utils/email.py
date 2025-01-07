#################################  S E N D  E M A I L  #################################
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def send_mails(email, name, password):
    username = email
    temporary_password = password
    subject = "Verify Your Naukri Account Email"

    text_content = f"""
        Dear {name},

        Welcome to Naukri! To ensure the security of your account and access all our features, please verify your email address.

        Click the following link to verify your email:
        {verification_link}

        This link will expire in 24 hours for security purposes.

        If you didn't create a Naukri account, please ignore this email.

        Best regards,
        Naukri Team
    """

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your Naukri Account</title>
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
                        background-color: #2196F3;
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
                        text-align: center;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #2196F3;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        margin: 20px 0;
                        font-weight: bold;
                    }}
                    .button:hover {{
                        background-color: #1976D2;
                    }}
                    .important {{
                        color: #2196F3;
                        font-weight: bold;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #777;
                    }}
                    .verification-icon {{
                        width: 80px;
                        height: 80px;
                        margin: 20px auto;
                        display: block;
                    }}
                    .info-box {{
                        background-color: #E3F2FD;
                        border: 1px solid #BBDEFB;
                        border-radius: 4px;
                        padding: 15px;
                        margin: 20px 0;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    Verify Your Naukri Account
                </div>
                <div class="content">
                    <svg class="verification-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="11" stroke="#2196F3" stroke-width="2"/>
                        <path d="M7 12L10 15L17 8" stroke="#2196F3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    
                    <h2>Welcome to Naukri!</h2>
                    <p>Dear {name},</p>
                    <p>Thank you for creating your Naukri account. To ensure the security of your account and access all our features, please verify your email address.</p>
                    
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                    
                    <div class="info-box">
                        <p><strong>Please Note:</strong></p>
                        <ul style="list-style-type: none; padding-left: 0;">
                            <li>• This verification link will expire in 24 hours</li>
                            <li>• If you didn't create a Naukri account, please ignore this email</li>
                        </ul>
                    </div>
                    
                    <p>If the button above doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; font-size: 12px; color: #666;">{verification_link}</p>
                </div>
                <div class="footer">
                    <p>This is an automated email, please do not reply.</p>
                    <p>&copy; 2024 Naukri. All rights reserved.</p>
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