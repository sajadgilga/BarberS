"""BarberS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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

    path('login/',CustomAuthToken.as_view()),
    path('signup/',views.signUp_view,name = 'sign up'),
    # path ('signup/',CustomSignUp.as_view()),
    # path('login/', v.obtain_auth_token),#built in view to obtain token  from given username and password
     # path('hello/',views.hello_world,name = 'hello_world'),
]
