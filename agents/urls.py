from django.urls import path
from .views import Dashboard,ClaimedTickets,UnclaimedTickets,TicketDetailView

app_name = "agents"

urlpatterns = [
    path("",Dashboard.as_view(),name="dashboard"),
    path("claimed/",ClaimedTickets.as_view(),name="claimed"),
    path("unclaimed/",UnclaimedTickets.as_view(),name="unclaimed"),
    path("ticket/<uuid:id>",TicketDetailView.as_view(),name="ticket_detail"),
]