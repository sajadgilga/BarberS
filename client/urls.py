from django.urls import path, include

from client.views.authentication import *
from client.views.main_page import *
from client.views.profile import *
from client.views.payment import *

app_name = 'client'
urlpatterns = [
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('change_profile/', customer_change_profile),
    path('barber_profile/', barber_profile),
    path('profile/', customer_profile),
    path('best_barbers/', BestBarbers.as_view()),
    path('closest_barbers/', ClosestBarbers.as_view()),
    path('home_page/', get_home_page),
    path('location/', CustomerLocationHandler.as_view()),
    path('locations/', get_locations),
    path('search_barbers/', SearchBarbers.as_view()),
    path('logout/', logout),
    path('get_like/', get_like),
    path('get_reserved_service/', get_reserved_service),
    path('discount/', discount),
    path('barber_comment/<str:barber_id>/', barber_comment),
    path('send_comment/', send_comment),
    path('customer_likes/', customer_likes),
    path('add_like/', add_like),
    path('request/', PaymentRequest.as_view()),
    path('verify/', verify),
    path('score/', score),

]
