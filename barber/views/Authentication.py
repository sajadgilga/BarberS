import random
# from random import random

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from BarberS.utils import get_error_obj
from client.models import LoginUser, Barber
from client.serializers import BarberSerializer, bar_BarberSerializer, BarberSerializer_out


@api_view(['GET'])
@permission_classes([AllowAny])
def login(request, phone=None):
    try:
        login_user = LoginUser.objects.filter(phone=phone)
        maincode = str(random.randrange(1000, 10000, 1))
        if len(login_user) == 0:
            LoginUser.objects.create(phone=phone, code=maincode)
        else:
            login_user = login_user.first()
            login_user.code = maincode
            login_user.save()
        return Response({maincode})
    except:
        return Response(get_error_obj('server_error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_verify(request):
    # try:
    if any(d not in request.data for d in ['phone', 'code', 'name', 'gender']):
        return Response(get_error_obj('wrong_parameters', 'name, gender, phone & code must be sent in body'),
                        status=status.HTTP_400_BAD_REQUEST)
    phone = request.data['phone']
    code = request.data['code']
    name = request.data['name']
    gender = request.data['gender']
    login_user = LoginUser.objects.filter(phone=phone).first()
    if login_user is None:
        return Response(get_error_obj('auth_no_code_found'),
                        status=status.HTTP_400_BAD_REQUEST)
    else:
        if login_user.code == code:
            user = User.objects.filter(username=phone).first()
            if user is None:
                user = User.objects.create(username=phone, password='password')
                id = Barber.objects.count() + 1
                barber = Barber(user=user, barber_id='barber_{}'.format(id), phone=phone)
                barber.gender = gender
                barber.name = name
                barber.save()
            else:
                barber = Barber.objects.filter(user=user).first()
                barber.gender = gender
                barber.name = name
                barber.save()
            token, create = Token.objects.get_or_create(user=user)
            serializer = BarberSerializer_out(barber)
            data = serializer.data
            # data['name'] = barber.name
            data['phone'] = barber.phone
            # data['id'] = barber.barber_id
            data['token'] = token.key
            return Response(data)

        else:
            return Response(get_error_obj('auth_wrong_code'), status=status.HTTP_400_BAD_REQUEST)
    # except:
    #     return Response(get_error_obj('auth_failure'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
