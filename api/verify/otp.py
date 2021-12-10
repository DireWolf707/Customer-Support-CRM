from fastapi import APIRouter,Depends,BackgroundTasks
from twilio.rest import Client
from . import schema
from utils import get_private_token_header,get_twilio_client
from config import get_settings
import time

settings = get_settings()

router = APIRouter(
    prefix="/2FA",
    tags=["2FA"],
)

def twilio_otp_call(client,to):
    client.verify.services(settings.twilio_service_id).verifications.create(to=to, channel='sms')
    
@router.post('/send')
async def send_otp(data : schema.SendRequest ,background_tasks: BackgroundTasks,client : Client = Depends(get_twilio_client)):
    background_tasks.add_task(twilio_otp_call ,client ,data.phone)
    return 'ok'


@router.post('/verify',dependencies=[Depends(get_private_token_header)],)
def verify_otp(data : schema.VerifyRequest , client : Client = Depends(get_twilio_client)):
    verification_check = client.verify.services(settings.twilio_service_id).verification_checks.create(to=data.phone, code=data.otp)
    return verification_check.status