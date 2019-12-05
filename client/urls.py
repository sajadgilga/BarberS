from django.urls import path,include
from client.views import CustomAuthToken, signUp_view

app_name ='client'
urlpatterns = [
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('signup/', signUp_view, name='sign up'),
]
