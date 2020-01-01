from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from client.serializers import *
from client.models import Barber, Customer, PresentedService


@api_view(['POST'])
@permission_classes([AllowAny])
def barber_profile(request):
    name = request.data['barber']
    if name is None:
        return Response("wrong name!", status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(firstName=name).first()  # it must changed!! because first name is common
    if barber is None:
        return Response("no barber with this information", status=status.HTTP_400_BAD_REQUEST)
    serializer = BarberSerializer_out(barber)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_profile(request):
    user = request.user
    if user is None:
        return Response("user not found ", status=status.HTTP_400_BAD_REQUEST)
    customer = Customer.objects.filter(user=request.user).first()
    if customer is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = CustomerSerializer_out(customer)
    return Response(serializer.data)


'''after authentication 
set Profile  for complete the user information
and save it to the data base 
'''


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_change_profile(request):
    # how make a field optional? set a default value or set required = false

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
        # return Response({str(serializer.errors)})
        return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_like(request):
    user = request.user
    if user is None:
        return Response({"user not found "}, status=status.HTTP_400_BAD_REQUEST)
    customer = Customer.objects.get(phone=user.username)
    if customer.isCompleted is False:
        return Response({"you must compelet your information", }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    barbers = Barber.objects.filter(customer__user__username=user.username)
    serializer = BarberSerializer_out(barbers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_reserved_service(request):
    user = request.user
    if user is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    customer = Customer.objects.get(phone=user.username)
    if customer.isCompleted is False:
        return Response({"you must compelet your information", }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    services = PresentedService.objects.filter(customer__user__username=user.username)
    serializer = PresentedServiceSerializer(services, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def discount(request):
    pass
    # serializer  = DiscountSerializer(data=request.data)
    # serializer.is_valid(raise_exception=True)
    # input_dicount = serializer.create(serializer.validated_data)
    # code = input_dicount.value
    # discount = Discount.objects.get(value = code)
    # if discount is None :
    #     return Response({"wrong discount code!!"},status=status.HTTP_400_BAD_REQUEST)
    # else : pass # what should i do?????????????????????????????????
    #
    #


'''api for getting comments a barber 
    it needs barber id '''


# TODO:handle if barberid is not given or if it is not a integer
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def barber_comment(request, barber_id):
    if barber_id is None:
        Response({"status": 402}, status.HTTP_400_BAD_REQUEST)  # barber id does not send
    barber = Barber.objects.filter(user__username=barber_id).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_404_NOT_FOUND)  # barber not exists:status 400
    try:
        comment = Comment.objects.filter(barber=barber).order_by('created_time')
    except:
        return Response({"status": 401}, status=status.HTTP_404_NOT_FOUND)
    serializer = CommentSerializer(comment, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


'''send comment api for add a comment by customer for barber
it takes barber username customer id and comment's text
no return '''


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def send_comment(request):
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.create(serializer.validated_data)
        if comment is None:
            return Response({"status": 402}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"status": 402}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_200_OK)


'''customer like api for showing liked barbers by customer 
it ruturns barbers infromaation'''


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def customer_likes(request):
    user = request.user
    if user is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    customer = Customer.objects.filter(phone=user.username).first()
    if customer is None:
        return Response({"status": 402}, status=status.HTTP_400_BAD_REQUEST)
    barbers = customer.like.all()
    serializer = BarberSerializer_out(barbers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


'''add like api for liking barbers
it gets barber username as parameter and no return value'''


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_like(request):
    user = request.user
    barber_username = request.data['barber_username']
    barber = Barber.objects.filter(user__username=barber_username).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    if user is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    customer = Customer.objects.filter(phone=user.username).first()
    if customer is None:
        return Response({"status": 402}, status=status.HTTP_400_BAD_REQUEST)
    customer.like.add(barber)
    return Response(status=status.HTTP_200_OK)

# 400 not exist
