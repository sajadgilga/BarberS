from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer,LoginUser
from django.contrib.auth.models import User
import random
from rest_framework.decorators import api_view, permission_classes, APIView, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponseNotAllowed
from django.shortcuts import  redirect

''' custom view for login and authentication .
    make a random 4 digits code 
    use get method to detect a duplicates phone number and
    post method to make a token
'''


class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone=None):
        login_user =LoginUser.objects.filter(phone = phone).first()
        maincode = str(random.randrange(1000, 10000, 1))


        msg = ""
        if login_user is None:
            # return Response({phone})

            login_user = LoginUser.objects.create(phone = phone , code = maincode)
            login_user.save()
            msg = "message sent !!"
        else:
            msg = "This phone has used"
            login_user.code = maincode
            login_user.save()
        return Response({msg})

    # username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        phone = request.data['phone']
        code = request.data['code']
        # checkking  is the phone number  in the database??
        # maincode = 1234;
        login_user = LoginUser.objects.filter(phone = phone ).first()
        if login_user is None :
            msg = "invalid phone number "#it would not happen because if the post body have a right phone number
            return redirect (request.path+phone)#or we can redirect to a get with a phone number
        maincode = login_user.code
        if maincode == code:
            user = User.objects.create_user(username=phone)
            token, create = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.pk})
        else:
            login_user.code = str(random.randrange(1000, 10000, 1))
            login_user.save()
            return Response({"false code!"})


'''after authentication 
set Profile  for complete the user information
and save it to the data base 
'''


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signUp_view(request):
    # how make a feild optional?
    # why we should give a self to a method ?

    phone = request.user.username

    first_name = request.data['firstname']
    last_name = request.data['lastname']
    snn = request.data['snn']
    gender = request.data['gender']
    location = request.data['location']
    image = request.data['image']

    if first_name is None or last_name is None or snn is None or gender is None:
        msg = {"status": 201}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    customer = Customer()
    customer.user = user
    customer.credit = 0
    customer.firstName = first_name
    customer.lastName = last_name
    customer.snn = snn
    customer.image = image
    customer.gender = gender
    customer.location = location
    customer.phone = phone

    if customer is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    else:
        customer.isCompleted = True
        customer.save()
        msg = {"status": 0}
        return Response({msg})
