from fastapi import HTTPException,Header
from twilio.rest import Client
import config,redis


settings = config.get_settings()

def get_private_token_header(private_token: str = Header(...)):
    if private_token != settings.app_secret:
        raise HTTPException(status_code=400, detail="Operation forbidden")

def get_twilio_client():
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)

def get_redis_client():
    return redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)