from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
import requests,os

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        phone = self.object.phone
        otp=self.request.POST['otp']
        api_key=os.environ.get("api_key","h435y8wfj3h24hy328r32b4h24j")

        resp = requests.post("http://127.0.0.1:8080/2FA/verify",
            json={
                "phone": phone,
                "otp": otp
            },headers={
                "private-token": api_key
            })

        if resp.json()=='approved':
            self.object.save()
            login(self.request,self.object)
            send_mail(
                subject='Welcome Aboard',
                message='Your account has been successfully registered with your mobile number!',
                from_email=None,
                recipient_list=[self.object.email],
                fail_silently=True,
            )
            return redirect("ticket:home")

        return self.render_to_response(self.get_context_data(form=form))