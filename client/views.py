from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from client.models import Customer
from django.contrib.auth.models import User
import random
from rest_framework.decorators import api_view,permission_classes,APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
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

        users = User.objects.get_queryset()
        for user in users:
            if  user.username is  phone:
                msg = "This phone has used"
                return Response({msg})
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def signUp_view(request):


        #is phone and code and token still in body or header ?
        #how make a feild optional?
        # why we should give a self to a method ?
        #how give a authorize to users?

    phone = request.user.username

    firstname = request.data['firstname']
    lastname = request.data['lastname']
    snn = request.data['snn']
    gender = request.data['gender']
    location = request.data['locatioan']
    credit = 0
    image = request.data['image']

    if (firstname is None or lastname is None or snn is None or gender is None):
        msg = "please enter required fields"
        return Response[{msg}]

    customer = Customer.concrete_model(firstname = firstname,lastname = lastname, snn = snn , gender = gender , phone = phone ,
                                               location = location, image= image, credit  = credit )


    if customer is  None :
         Customer.delete(customer)
         return Response({"mistake in data"})

    else :
        msg = "succesfully signed up"
        return Response({msg})

    # return  Response({"dkja"})
#
# class CustomSignUp(APIView):
#     permission_classes([AllowAny])
#     def post(self,request):
#         pass
#     def get (self,request):
#         return Response({"this is get test"});







# {
# 	"firstname":"behnam",
# 	"lastname":"beigi",
# 	"snn":"2158998",
# 	"gender":"m",
# 	"location":"",
# 	"image":""
# }