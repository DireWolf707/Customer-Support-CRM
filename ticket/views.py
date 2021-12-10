from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MessageTicketForm,CallTicketForm

class HomeView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request,"home/home.html",{"mform":MessageTicketForm(),"cform":CallTicketForm()})
    
    def post(self,request,*args,**kwargs):
        data = request.POST
        if data['type'] == 'text':
            form = MessageTicketForm(data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.lead = request.user
                ticket.save()
        else:
            form = CallTicketForm(data)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.lead = request.user
                ticket.by_call = True
                ticket.save()
        return redirect("ticket:home")