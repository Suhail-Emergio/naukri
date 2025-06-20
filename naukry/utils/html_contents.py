#################################  G E N E R A T E  H T M L  C O N T E N T S  #################################
from django.conf import settings
from .email import send_mails

project_name = settings.PROJECT_NAME

async def verify_mail(email, name, password):
    subject = f"Verify Your {project_name} Account Email"

    text_content = f"""
        Dear {name},

        Welcome to {project_name}! To ensure the security of your account and access all our features, please verify your email address.

        Verification code is:
        {password}

        This link will expire in 24 hours for security purposes.

        If you didn't create a {project_name} account, please ignore this email.

        Best regards,
        {project_name} Team
    """

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your {project_name} Account</title>
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
                    Verify Your {project_name} Account
                </div>
                <div class="content">
                    <svg class="verification-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="11" stroke="#2196F3" stroke-width="2"/>
                        <path d="M7 12L10 15L17 8" stroke="#2196F3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    
                    <h2>Welcome to {project_name}!</h2>
                    <p>Dear {name},</p>
                    <p>Thank you for creating your {project_name} account. To ensure the security of your account and access all our features, please verify your email address.</p>
                    
                    <h2>OTP: {password}</h2>
                    
                    <div class="info-box">
                        <p><strong>Please Note:</strong></p>
                        <ul style="list-style-type: none; padding-left: 0;">
                            <li>• This otp will expire in 60 seconds</li>
                            <li>• If you didn't create a {project_name} account, please ignore this email</li>
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated email, please do not reply.</p>
                    <p>&copy; 2024 {project_name}. All rights reserved.</p>
                </div>
            </body>
        </html>
    """

    await send_mails(subject=subject, content=text_content, html=html_content, email=email)

async def send_creds(email, password, username):
    subject = f"{project_name} Account Credentials"

    text_content = f"""
        Dear User,

        Welcome to {project_name}! This is an important message regarding your {project_name} account.
        For security reasons, we recommend changing your password upon your first login.
        If you didn't request this change, please contact our support team immediately.

        Best regards,
        {project_name} Team
    """

    html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your {project_name} Account</title>
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
                    {project_name} Account Credentials
                </div>
                <div class="content">
                    <svg class="verification-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="11" stroke="#2196F3" stroke-width="2"/>
                        <path d="M7 12L10 15L17 8" stroke="#2196F3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    
                    <h2>Welcome to {project_name}!</h2>
                    <p>Dear user,</p>
                    <p>Thank you for creating your {project_name} account. To ensure the security of your account and access all our features, please login to your account using email and password provided.</p>
                    
                    <ul>
                        <li><strong>Username:</strong> {username}</li>
                        <li><strong>Temporary Password:</strong> {password}</li>
                    </ul>

                </div>
                <div class="footer">
                    <p>This is an automated email, please do not reply.</p>
                    <p>&copy; 2024 {project_name}. All rights reserved.</p>
                </div>
            </body>
        </html>
    """

    await send_mails(subject=subject, content=text_content, html=html_content, email=email)