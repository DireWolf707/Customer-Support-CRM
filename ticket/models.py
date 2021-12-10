from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Ticket(models.Model):
    class ContactPreferences(models.TextChoices):
        MAIL = 'M', 'Mail'
        CALL = 'C', 'Call'
        SMS = 'S', 'Sms'
        WHATSAPP = 'W', 'Whatsapp'
    
    class Status(models.TextChoices):
        UNCLAIMED = 'UC', 'Unclaimed'
        CLAIMED = 'CL', 'Claimed'
        ClOSED = 'CD', 'Closed'


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    lead = models.ForeignKey(User,on_delete=models.CASCADE,related_name='lead_tickets')
    agent = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='agent_tickets',null=True,blank=True)
    description = models.TextField()
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True,blank=True)
    contact_preference = models.CharField(choices=ContactPreferences.choices,max_length=1,blank=True,null=False)
    status=models.CharField(choices=Status.choices,max_length=2,default=Status.UNCLAIMED)
    by_call=models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.id)
