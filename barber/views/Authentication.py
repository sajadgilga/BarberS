from random import random
from rest_framework import status
from rest_framework.response import Response
from client.models import Customer, LoginUser, Barber
from django.contrib.auth.models import User, AnonymousUser
import random
from rest_framework.decorators import api_view, permission_classes, APIView, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token


@api_view(['GET'])
@permission_classes([AllowAny])
def login(request, phone=None):
    try:
        login_user = LoginUser.objects.filter(phone=phone).first()
        maincode = str(random.randrange(1000, 10000, 1))
        if login_user is None:
            LoginUser.objects.create(phone=phone, code=maincode)
        else:
            login_user.code = maincode
            login_user.save()
        return Response({maincode})
    except:
        return Response({"status": 120}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_verify(request):
    try:
        phone = request.data['phone']
        code = request.data['code']
        login_user = LoginUser.objects.filter(phone=phone).first()
        if login_user is None:
            return Response({"status": 103},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            if login_user.code == code:
                user = User.objects.create(username=phone, password='password')
                id = Barber.objects.count() + 1
                barber = Barber(user=user, barber_id='barber_{}'.format(id), phone=phone)
                barber.save()
                token, create = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})

            else:
                return Response({"status": 101}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"status": 120}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
