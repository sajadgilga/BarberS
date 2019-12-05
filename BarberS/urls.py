from django.contrib import admin
from django.urls import path
from client import views
# from myapi.core import views
from rest_framework import views as v

from client.views import CustomAuthToken

app_name = 'client'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/<str:phone>/', CustomAuthToken.as_view()),

    path('login/', CustomAuthToken.as_view()),
    path('signup/', views.signUp_view, name='sign up'),
]
