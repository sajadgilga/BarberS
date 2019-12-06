from django.urls import path, include

from client.views.authentication import *
from client.views.main_page import *

app_name = 'client'
urlpatterns = [
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('signup/', signUp_view, name='sign up'),
    path('best_barbers/', best_barbers)
]
