from django import forms
from django.db import models
from .models import Ticket

class MessageTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('description','contact_preference')

class CallTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('contact_preference',)