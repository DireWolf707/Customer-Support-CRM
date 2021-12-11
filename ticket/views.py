import requests
from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .forms import MessageTicketForm,CallTicketForm
from django.core.mail import send_mail
from django.conf import settings


class HomeView(LoginRequiredMixin,UserPassesTestMixin,View):
    def test_func(self):
        return not self.request.user.is_staff

    def get(self,request,*args,**kwargs):
        return render(request,"home/home.html",{"mform":MessageTicketForm(),"cform":CallTicketForm()})
    
    def post(self,request,*args,**kwargs):
        valid =False
        data = request.POST
        if data['type'] == 'text':
            form = MessageTicketForm(data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.lead = request.user

                requests.post("http://127.0.0.1:8080/thirdparty/ticket/chat",
                json={
                    "text": ticket.description,
                    "ticket_id": str(ticket.id)
                },headers={
                    "private-token": settings.API_KEY
                })

                ticket.save()
                valid =True
                
        else:
            form = CallTicketForm(data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.lead = request.user
                ticket.by_call = True
                ticket.call_sid = requests.post("http://127.0.0.1:8080/thirdparty/ticket/voice",
                json={
                    "phone": request.user.phone,
                },headers={
                    "private-token": settings.API_KEY
                })

                ticket.save()
                valid =True

        if False:
            send_mail(
                    subject='Support Ticket Opened!',
                    message=f'Your Support Ticket #{ticket.id} is opened and someone from our team will contact you shortly!',
                    from_email=None,
                    recipient_list=[self.request.user.email],
                    fail_silently=True,
                )
        return redirect("ticket:home")