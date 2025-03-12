#################################  P U S H  N O T I F I C A T I O N  #################################
from onesignal_sdk.client import Client
from onesignal_sdk.client import AsyncClient
from django.conf import settings
from asgiref.sync import sync_to_async

def send_notifications(subject, title, onesignal_id):
    try:
        client = Client(app_id=settings.ONESIGNAL_APP_ID, rest_api_key=settings.ONESIGNAL_API_KEY)
        notification_body = {
            "headings": {"en": title},
            "contents": {"en": subject},
            "include_player_ids": [onesignal_id]
        }
        response = client.send_notification(notification_body)
        print(f"Notification sent successfully. SID: {response}")
    except Exception as e:
        return None