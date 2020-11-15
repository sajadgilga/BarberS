import random

from django.contrib.auth.models import User, AnonymousUser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from BarberS.utils import get_error_obj
from client.models import Customer, LoginUser
from client.serializers import CustomerSerializer

''' custom view for login and authentication .
    make a random 4 digits code 
    use get method to detect a duplicates phone number and
    post method to make a token
    also for useres that loed out make a new token (in the post method )
'''


class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone=None):
        try:
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
        except:
            return Response(get_error_obj('auth_failure'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data['phone']
            code = request.data['code']
            login_user = LoginUser.objects.filter(phone=phone).first()
            if login_user is None:
                return Response(get_error_obj('auth_no_code_found'),
                                status=status.HTTP_400_BAD_REQUEST)  # or we can redirect to a get with a phone number
            maincode = login_user.code
            if maincode == code:
                user = User.objects.filter(username=phone).first()
                if not user:
                    user = User.objects.create(username=phone, password='password')
                    id = Customer.objects.count() + 1
                    customer = Customer(user=user, phone=phone, customer_id='customer_{}'.format(id))
                    customer.save()
                else:
                    customer = Customer.objects.filter(user=user).first()
                token, create = Token.objects.get_or_create(user=user)
                serializer = CustomerSerializer(customer)
                data = serializer.data
                data['name'] = customer.firstName + ' ' + customer.lastName
                data['phone'] = customer.phone
                data['id'] = customer.customer_id
                data['token'] = token.key
                return Response(data)
            else:
                return Response(get_error_obj('auth_wrong_code'), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(get_error_obj('auth_failure'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


''' get method for logout . it takes a token in header and delete the token '''


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def logout(request):
    try:
        user = request.user
        if user is AnonymousUser:
            return Response(get_error_obj('access_denied'), status.HTTP_404_NOT_FOUND)
        user.auth_token.delete()
        return Response({"status": 200}, status=status.HTTP_200_OK)
    except:
        return Response(get_error_obj('server_error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
