from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
import random
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import  HttpResponseNotAllowed
''' custom view for login and authentication .
    make a random 4 digits code 
'''
class CustomAuthToken(ObtainAuthToken):
    def get(self, request, phone):
        return Response({phone})
#username and pass will send with a post method
    def post(self, request, *args, **kwargs):
        #                                    context={'request': request})


        # serializer = self.serializer_class(data=request.data,
        # serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data['user']
        # phone = request.data['phone']
        # code = request.data['code'];
        phone = request.POST.get("phone","")
        code =  request.POST.get("code","")
        # maincode = random.randrange(1000,10000,1)
        maincode = code
        if maincode == code :
            user = authenticate(request,username=phone,password =code)
            token,create = Token.objects.get_or_create(user = user)
            return Response({
                'token': token.key,
                'user_id' :phone
            })
        else:
            return HttpResponseNotAllowed

