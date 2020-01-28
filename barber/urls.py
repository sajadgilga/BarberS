from django.urls import path, include
from barber.views.Authentication import *
from barber.views.profile import *

app_name = 'barber'
urlpatterns = [
    path('login/<str:phone>/', login),
    path('login_verify/', login_verify),
    path('get_comment/', get_comment),
    path('get_profile/', get_profile),
    path('change_profile/', change_profile),
    path('get_home/', Get_home.as_view()),
    path('add_sample/', add_samples),
    path('shift_handler/', shift_handler),
]
