from django.urls import path

from client.views import CustomAuthToken, signUp_view

urlpatterns = [
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('signup/', signUp_view, name='sign up'),
]
