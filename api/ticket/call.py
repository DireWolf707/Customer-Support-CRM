from fastapi import APIRouter,Depends,BackgroundTasks,Request,Form
from utils import get_private_token_header,get_twilio_client
from config import get_settings
from . import schema
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import symbl

settings = get_settings()
PUBLIC_URL = "http://9b26-125-99-204-108.ngrok.io"

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
    # REDIS ticket_id=conversation_object.get_conversation_id()

@ticket_router.post("/chat",dependencies=[Depends(get_private_token_header)])
async def chat_ticket(data : schema.TextTicket ,background_tasks: BackgroundTasks):
    background_tasks.add_task(symbl_text ,data.text,data.ticket_id)
    return 'ok'


@ticket_router.post("/voice",dependencies=[Depends(get_private_token_header)])
async def voice_ticket(data : schema.CallTicket,client : Client = Depends(get_twilio_client)):
    # automated voice
    response = VoiceResponse()
    response.say("""
    Call will disconnect automatically in case of silence.
    You can record your message after the beep and stop recording by pressing 0.
    """,voice="man")
    response.record(timeout=6,play_beep=True,finishOnKey="0",
    action=None,recordingStatusCallback=PUBLIC_URL+"/thirdparty/ticket/recording_hook",
    recordingStatusCallbackMethod="POST",recordingStatusCallbackEvent="completed")
    response.hangup()
    # create call
    call = client.calls.create(
        to=data.phone,
        from_='+12087389728',
        twiml=response.to_xml(),
    )
    return call.sid

def symbl_voice(CallSid,RecordingUrl):
    app_id=settings.symbl_app_id
    app_secret=settings.symbl_app_secret
    credentials={"app_id": app_id, "app_secret": app_secret}
    conversation_object = symbl.Audio.process_url(
        payload={
            'url':RecordingUrl, 
            'detectPhrases': True, 
            },
            credentials=credentials,
            wait=False,
        )
    # REDIS callsid:recording_url=recording_url
    # REDIS callsid:symbl_id=conversation_object.get_conversation_id()


@ticket_router.post("/recording_hook")
async def recording_hook(background_tasks: BackgroundTasks,request: Request,
    CallSid:str =  Form(...),
    RecordingUrl:str =  Form(...),
    ):
    background_tasks.add_task(symbl_voice,CallSid,RecordingUrl)
    return 'ok'