from django.shortcuts import redirect, render,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from ticket.models import Ticket,Status
from django.conf import settings
from django.utils import timezone
import redis,symbl

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class AgentTest(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class Dashboard(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        claimed_tickets = redis_client.get(f"claimed_tickets:{request.user.id}")
        closed_tickets = redis_client.get(f"closed_tickets:{request.user.id}")
        call_taken = redis_client.get(f"call_taken:{request.user.phone}")
        context['claimed_tickets']= claimed_tickets.decode("utf-8") if claimed_tickets else 0
        context['closed_tickets']= closed_tickets.decode("utf-8") if closed_tickets else 0
        context['call_taken']= call_taken.decode("utf-8") if call_taken else 0
        return render(request,'agents/dashboard.html',context=context)
    
class ClaimedTickets(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        context['tickets']=Ticket.objects.filter(agent=request.user,status=Status.CLAIMED)
        return render(request,'agents/claimed.html',context=context)

class UnclaimedTickets(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        context['tickets']=Ticket.objects.filter(status=Status.UNCLAIMED)
        return render(request,'agents/unclaimed.html',context=context)
    
    def post(self,request,*args,**kwargs):
        ticket = get_object_or_404(Ticket,id=request.POST.get("ticket_id"))
        ticket.agent = request.user
        ticket.status = Status.CLAIMED
        ticket.save()
        redis_client.incr(f"claimed_tickets:{request.user.id}")
        return redirect("agents:ticket_detail",ticket.id)

class TicketDetailView(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        ticket = get_object_or_404(
            Ticket,id=kwargs['id'],status=Status.CLAIMED,agent=request.user
        )
        context['ticket'] = ticket
        context['lead'] = ticket.lead
        credentials={"app_id": settings.SYMBL_APP_ID, "app_secret": settings.SYMBL_APP_SECRET}

        if ticket.by_call:
            voice_url = redis_client.get(f"voice:record:{ticket.call_sid}")
            context['voice_url'] = voice_url.decode("utf-8") if voice_url else None

            symbl_conv_id = redis_client.get(f"voice:symbl:{ticket.call_sid}")
            context['analytics'] = symbl_conv_id.decode("utf-8") if symbl_conv_id else None
            context['messages'] = list()
            messages = symbl.Conversations.get_messages(conversation_id=context['analytics'],credentials=credentials)
            for message in messages.to_dict()['messages']:
                context['messages'].append(message['text'])
            
            context['topics'] = list()
            topics = symbl.Conversations.get_topics(conversation_id=context['analytics'],credentials=credentials)
            for topic in topics.to_dict()['topics']:
                context['topics'].append(topic['text'])
            

        else:
            symbl_conv_id = redis_client.get(f"chat:{ticket.id}")
            context['analytics'] = symbl_conv_id.decode("utf-8") if symbl_conv_id else None
            context['topics'] = list()
            topics = symbl.Conversations.get_topics(conversation_id=context['analytics'],credentials=credentials)
            for topic in topics.to_dict()['topics']:
                context['topics'].append(topic['text'])

        return render(request,'agents/ticket_detail.html',context=context) 

    def post(self,request,*args,**kwargs):
        ticket = get_object_or_404(
            Ticket,id=kwargs['id'],status=Status.CLAIMED,agent=request.user
        )
        ticket.close_time = timezone.now()
        ticket.status = Status.ClOSED
        ticket.save()
        redis_client.incr(f"closed_tickets:{request.user.id}")
        return redirect("agents:dashboard") 
