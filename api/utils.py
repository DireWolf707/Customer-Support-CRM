from fastapi import HTTPException,Header
from twilio.rest import Client
import config


settings = config.get_settings()

def get_private_token_header(private_token: str = Header(...)):
    if private_token != settings.app_secret:
        raise HTTPException(status_code=400, detail="Operation forbidden")

def get_twilio_client():
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)