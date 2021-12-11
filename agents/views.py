from django.shortcuts import redirect, render,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from ticket.models import Ticket,Status
from django.conf import settings

import redis
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class AgentTest(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class Dashboard(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        call_taken = redis_client.get(f"call_taken:{request.user.id}")
        context['claimed_tickets']=Ticket.objects.filter(agent=request.user,status=Status.CLAIMED).count()
        context['closed_tickets']=Ticket.objects.filter(agent=request.user,status=Status.ClOSED).count()
        context['call_taken']= call_taken if call_taken else 0
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
        return redirect("agents:ticket_detail",ticket.id)

class TicketDetailView(LoginRequiredMixin,AgentTest,View):
    def get(self,request,*args,**kwargs):
        context = dict()
        context['ticket'] = get_object_or_404(
            Ticket,id=kwargs['id'],status=Status.CLAIMED,agent=request.user
        )
        return render(request,'agents/ticket_detail.html',context=context) 
