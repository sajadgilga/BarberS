from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer, LoginUser
from django.contrib.auth.models import User
import random
from rest_framework.decorators import api_view, permission_classes, APIView, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from client.serializers import CustomerSerializer


class CustomAuthToken(ObtainAuthToken):
    """ custom view for login and authentication .
        make a random 4 digits code
        use get method to detect a duplicates phone number and
        post method to make a token
    """

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
        # checkking  is the phone number  in the database??
        # maincode = 1234;
        login_user = LoginUser.objects.filter(phone=phone).first()
        if login_user is None:
            msg = "invalid phone number "  # it would not happen because if the post body have a right phone number
            return redirect(request.path + phone)  # or we can redirect to a get with a phone number
        maincode = login_user.code
        if maincode == code:
            user = User.objects.filter(username=phone).first()
            if not user:
                user = User.objects.create(username=phone, password='password')
            customer = Customer.objects.get_or_create(user=user, phone=phone, firstName="customer")
            token, create = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.pk})
        else:
            login_user.code = str(random.randrange(1000, 10000, 1))
            login_user.save()
            return Response({"false code!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signUp_view(request):
    """after authentication
    set Profile  for complete the user information
    and save it to the data base
    """

    phone = request.user.username
    customer = Customer.objects.filter(phone=phone).first()
    # customer.image = request.data['image']
    if customer is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.update(customer, serializer.validated_data)
        customer.isCompleted = True
        return Response(status.HTTP_200_OK)

    else:
        return Response({str(serializer.errors)})
