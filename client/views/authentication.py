from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer, LoginUser, Barber
from django.contrib.auth.models import User, AnonymousUser
import random
from rest_framework.decorators import api_view, permission_classes, APIView, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from client.serializers import CustomerSerializer

''' custom view for login and authentication .
    make a random 4 digits code 
    use get method to detect a duplicates phone number and
    post method to make a token
    also for useres that loged out make a new token (in the post method )
'''


class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone=None):
        login_user = LoginUser.objects.filter(phone=phone).first()
        maincode = str(random.randrange(1000, 10000, 1))

        msg = ""
        if login_user is None:
            login_user = LoginUser.objects.create(phone=phone, code=maincode)
            login_user.save()
            msg = "message sent !!"
        else:
            msg = "This phone has used"
            login_user.code = maincode
            login_user.save()
        return Response({maincode})

    # username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        phone = request.data['phone']
        code = request.data['code']
        temp_user = User.objects.filter(username=phone).first()
        if temp_user is not None:
            token, create = Token.objects.get_or_create(user=temp_user)
            return Response({'token': token.key,
                             'user_id': temp_user.pk})
        # checkking  is the phone number  in the database??
        # maincode = 1234;
        login_user = LoginUser.objects.filter(phone=phone).first()
        if login_user is None:
            msg = "invalid phone number "  # it would not happen because if the post body have a right phone number
            return redirect(request.path + phone)  # or we can redirect to a get with a phone number
        maincode = login_user.code
        if maincode == code:
            user, temp = User.objects.get_or_create(username=phone, password='password')
            id = Customer.objects.count() + 1
            customer = Customer.objects.create(user=user, phone=phone, customer_id='customer_{}'.format(id))
            token, create = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.pk})
        else:
            login_user.code = str(random.randrange(1000, 10000, 1))
            login_user.save()
            return Response({"false code!"})


''' get method for logout . it takes a token in header and delete the token '''


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def logout(request):
    user = request.user
    if user is AnonymousUser:
        return Response("user not found ", status.HTTP_404_NOT_FOUND)
    user.auth_token.delete()
    return Response("succesfull loged out ", status=status.HTTP_200_OK)
