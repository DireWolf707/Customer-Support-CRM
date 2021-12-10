from django.views import View
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request,"home/home.html")
    
    def post(self,request,*args,**kwargs):
        print(request.POST)
        data = request.POST
        if data['type'] == 'text':
            print("text message receicve",data['message'])
        else:
            print("text voice request")
        return render(request,"home/home.html")