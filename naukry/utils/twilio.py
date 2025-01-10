#################################  T W I L I O  I N T E G R A T I O N  #################################
import json
import asyncio
from twilio.rest import Client
from django.conf import settings
from asgiref.sync import async_to_sync
from django.http import JsonResponse

def send_otp(otp, number):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        content_sid="HX74f435f5b9a65118273b98cddd6bfc01",
        from_='whatsapp:+917594088814',
        to=f'whatsapp:+91{number}',
        content_variables=json.dumps({"1": str(otp)}),
    )
    print(f"Message sent with SID: {message.sid}")

def send_updates(body, number):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        # content_sid="HX745a5f3373407b031007738f57b6ceb6",
        content_sid="HX2c2d60626811876c3f71b2112405047d",
        from_='whatsapp:+917594088814',
        to=f'whatsapp:+91{number}',
        content_variables=json.dumps({"1": body}),
    )
    print(f"Message sent with SID: {message.sid}")

async def whatsapp_message(otp, number):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, send_otp, otp, number)