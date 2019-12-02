from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer

from django.contrib.auth.models import User
import random
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponseNotAllowed

''' custom view for login and authentication .
    make a random 4 digits code 
'''


class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone=None):
        return Response({phone})

    # username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        phone = request.data['phone']
        code = request.data['code']
        maincode = random.randrange(1000, 10000, 1)
        if maincode == code:
            user = User.objects.create_user(username=phone, password=code)  # in the parameter don't have self!!
            token, create = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.pk})

        else:
            return Response(status=403)

    # def signUp_view(request):
    #     pass

