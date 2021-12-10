import django
from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MessageTicketForm,CallTicketForm
from django.core.mail import send_mail


class HomeView(LoginRequiredMixin,View):
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
                ticket.save()
                valid =True
                
        else:
            form = CallTicketForm(data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.lead = request.user
                ticket.by_call = True
                ticket.save()
                valid =True

        if valid:
            send_mail(
                    subject='Support Ticket Opened!',
                    message=f'Your Support Ticket #{ticket.id} is opened and someone from our team will contact you shortly!',
                    from_email=None,
                    recipient_list=[self.request.user.email],
                    fail_silently=True,
                )
        return redirect("ticket:home")