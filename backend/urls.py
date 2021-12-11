from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('agent/', include('agents.urls',namespace="agents")),
    path('', include('ticket.urls',namespace="ticket")),
]
