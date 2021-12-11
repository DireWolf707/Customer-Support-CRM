import requests
from fastapi import APIRouter,Depends,BackgroundTasks,Request
from utils import get_private_token_header,get_twilio_client
from config import get_settings
from . import schema
from twilio.twiml.voice_response import VoiceResponse
import symbl

settings = get_settings()
PUBLIC_URL = "http://fee0-125-99-204-142.ngrok.io"

ticket_router = APIRouter(
    prefix="/thirdparty/ticket",
    tags=["ticket"],

)

def symbl_text(text,ticket_id):
    app_id=settings.symbl_app_id
    app_secret=settings.symbl_app_secret
    credentials={"app_id": app_id, "app_secret": app_secret}
    request_body ={
    "name": "Support Ticket",
    "detectPhrases": True,
    "messages": [
        {
        "payload": {
            "content": text,
            "contentType": "text/plain"
        },
        }
    ]
    }
    conversation_object = symbl.Text.process(payload=request_body,wait=False,credentials=credentials)
    # STORE IN REDIS in BACKGROUND conversation_object.get_conversation_id()

@ticket_router.post("/chat",dependencies=[Depends(get_private_token_header)])
async def chat_ticket(data : schema.TextTicket ,background_tasks: BackgroundTasks):
    background_tasks.add_task(symbl_text ,data.text,data.ticket_id)
    return 'ok'



def send_call(phone : str):
    client = get_twilio_client()
    # automated voice
    response = VoiceResponse()
    response.say("""
    Call will disconnect automatically in case of silence.
    You can record your message after the beep and stop recording by pressing 0.
    """,voice="man")
    response.record(timeout=6,play_beep=True,finishOnKey="0")
    response.hangup()
    # create call
    client.calls.create(
        to=phone,
        from_='+12087389728',
        twiml=response.to_xml(),
        status_callback = PUBLIC_URL+"/thirdparty/ticket/recording_hook",
    )


@ticket_router.post("/voice",dependencies=[Depends(get_private_token_header)])
async def voice_ticket(data : schema.CallTicket,background_tasks: BackgroundTasks):
    background_tasks.add_task(send_call ,data.phone)
    return 'ok'


@ticket_router.post("/recording_hook")
async def recording_hook(background_tasks: BackgroundTasks,request: Request):
    #background_tasks.add_task()
    data = await request.json()
    print(data)
    return 'ok'