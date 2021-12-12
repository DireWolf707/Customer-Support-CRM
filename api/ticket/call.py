from fastapi import APIRouter,Depends,BackgroundTasks,Form,Response
from utils import get_private_token_header,get_twilio_client,get_redis_client
from config import get_settings
from . import schema
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import symbl

settings = get_settings()
PUBLIC_URL = "http://6d90-60-254-105-91.ngrok.io"

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
    redis_client = get_redis_client()
    redis_client.set(f"chat:{ticket_id}",conversation_object.get_conversation_id())

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
    """,voice="alice")
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
    redis_client = get_redis_client()
    redis_client.set(f"voice:symbl:{CallSid}",conversation_object.get_conversation_id())
    redis_client.set(f"voice:record:{CallSid}",RecordingUrl)


@ticket_router.post("/recording_hook")
async def recording_hook(
    background_tasks: BackgroundTasks,
    CallSid:str =  Form(...),
    RecordingUrl:str =  Form(...),
    ):
    background_tasks.add_task(symbl_voice,CallSid,RecordingUrl)
    return 'ok'


@ticket_router.post("/call_hook")
async def call_hook():
    response = VoiceResponse()
    response.say("""
    Your call is currently being connected to an agent.
    Please wait.
    """,voice="man")
    response.redirect(PUBLIC_URL+"/thirdparty/ticket/connect_agent_hook")
    return Response(content=str(response), media_type="application/xml")

@ticket_router.post("/connect_agent_hook")
async def connect_agent_hook():
    response = VoiceResponse()
    redis_client = get_redis_client()
    agent = redis_client.blpop('agents',5)
    if agent:
        response.dial(
            agent[1].decode("utf-8"),
            action=PUBLIC_URL+"/thirdparty/ticket/connect_agent_callback_hook",
        )
        response.say('Goodbye')
        response.hangup()
    else:
        response.say("""
        Sorry no agent is currenty available to take your call.
        Please call back later or open a support ticket.
        """)
    return Response(content=str(response), media_type="application/xml")


def add_agent_to_queue(call_id):
    client = get_twilio_client()
    redis_client = get_redis_client()
    agent_phone = client.calls.get(call_id).fetch().to
    redis_client.rpush('agents',agent_phone)
    redis_client.incr(f"call_taken:{agent_phone}")


@ticket_router.post("/connect_agent_callback_hook")
async def connect_agent_callback_hook(
    background_tasks: BackgroundTasks,
    DialCallSid:str =  Form(...),
    ):
    background_tasks.add_task(add_agent_to_queue,DialCallSid)
    
    response = VoiceResponse()
    response.say('Goodbye')
    response.hangup()
    return Response(content=str(response), media_type="application/xml")