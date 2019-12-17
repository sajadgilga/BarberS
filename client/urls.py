from django.urls import path, include

from client.views.authentication import *
from client.views.main_page import *

app_name = 'client'
urlpatterns = [
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('signup/', signUp_view, name='sign up'),
    path('best_barbers/', BestBarbers.as_view()),
    path('closest_barbers/', ClosestBarbers.as_view()),
    path('location/', CustomerLocationHandler.as_view())
]
