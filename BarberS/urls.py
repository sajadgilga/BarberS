from django.contrib import admin
from django.urls import path, include
from client.views import CustomAuthToken, signUp_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path('login/<str:phone>/', CustomAuthToken.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('signup/', signUp_view, name='sign up'),
]
