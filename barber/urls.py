from django.urls import path, include
from barber.views.Authentication import *

app_name = 'barber'
urlpatterns = [
    path('login/<str:phone>/', login),
    path('login_verify/', login_verify)
]
