from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer
from django.contrib.auth.models import User
import random
from rest_framework.decorators import api_view,permission_classes,APIView,authentication_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponseNotAllowed

''' custom view for login and authentication .
    make a random 4 digits code 
    use get method to detect a duplicates phone number and
    post method to make a token
'''


class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone=None):
        users = User.objects.get_queryset()
        for user in users:
            if user.username == str(phone):
                msg = "This phone has used"
                return Response({msg})
        return Response({phone})

    # username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        phone = request.data['phone']
        code = request.data['code']


        # checkking  is the phone number  in the database??

        # maincode = random.randrange(1000, 10000, 1)
        maincode = 1234;
        if maincode == code:
            user = User.objects.create_user(username=phone, password=code)  # in the parameter don't have self!!
            token, create = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,
                             'user_id': user.pk})

        else:
            # return Response(status=403)
            return Response({"false code!"})
        '''after authentication 
        set Profile  for complete the user information
        and save it to the data base 
        '''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signUp_view(request):


        #how make a feild optional?
        # why we should give a self to a method ?

    phone = request.user.username

    firstname = request.data['firstname']
    lastname = request.data['lastname']
    snn = request.data['snn']
    gender = request.data['gender']
    location = request.data['location']
    image = request.data['image']

    if (firstname is None or lastname is None or snn is None or gender is None):
        msg = "please enter required fields"
        return Response[{msg}]

    user = request.user
    customer =Customer()
    customer.user=user;
    customer.credit =0;
    customer.firstName= firstname;
    customer.lastName =lastname
    customer.snn = snn
    customer.image = image
    customer.gender = gender
    customer.location=location
    customer.phone = phone



    if customer is  None :
         Customer.delete(customer)
         return Response({"mistake in data"})

    else :
        customer.isCompleted =True
        customer.save()
        msg = "succesfully signed up"
        return Response({msg})







# {
# 	"firstname":"behnam",
# 	"lastname":"beigi",
# 	"snn":"2158998",
# 	"gender":"m",
# 	"location":"",
# 	"image":""
# }