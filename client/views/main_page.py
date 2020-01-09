import json
from random import randint

from django.contrib.auth.models import User
# from django.contrib.gis.geos import Point
from django.db.models import F, ExpressionWrapper, CharField, Q, Sum
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS.settings import LOCATION_SEPARATOR
from client.models import Barber, Customer, Location
from client.serializers import BarberSerializer, LocationSerializer
from client.serializers import BarberRecordSerializer


class BestBarbers(APIView):
    """
    API to get best barbers according to their points
    """
    permission_classes = [IsAuthenticated]
    queryset = Barber.objects.all().order_by('-point')
    serializer_class = BarberRecordSerializer
    LIMIT = 10

    def get(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        offset = request.GET.get('offset')
        if not offset:
            offset = 0
        offset = self.LIMIT * int(offset)
        size = self.queryset.count()
        if offset > size:
            return Response({"status": 301}, status=status.HTTP_400_BAD_REQUEST)
        elif offset + self.LIMIT < size:
            barbers = self.queryset[offset: offset + self.LIMIT]
        else:
            barbers = self.queryset[offset:]
        user_location = customer.location.filter(chosen=True).first()
        barbers = self.serializer_class(barbers, many=True,
                                        context={"user_location": user_location.location})
        return Response(barbers.data)


class ClosestBarbers(APIView):
    """
    API to get closest barbers to customer
    """
    permission_classes = [IsAuthenticated]
    queryset = Barber.objects.all()
    serializer_class = BarberRecordSerializer
    LIMIT = 10

    @staticmethod
    def cal_dist(user_location, barber_location):
        if user_location == '' or barber_location == '':
            return -1
        [user_long, user_lat] = user_location.split(LOCATION_SEPARATOR)
        [barber_long, barber_lat] = barber_location.split(LOCATION_SEPARATOR)
        p1 = Point(float(user_long), float(user_lat))
        p2 = Point(float(barber_long), float(barber_lat))
        d = p1.distance(p2)
        return d * 10 ** 5

    def get(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        customer_location = customer.location.filter(chosen=True).first()
        queryset = sorted(self.queryset.all(),
                          key=lambda barber: ClosestBarbers.cal_dist(customer_location.location, barber.location))

        offset = request.GET.get('offset')
        if not offset:
            offset = 0
        offset = self.LIMIT * int(offset)
        size = self.queryset.count()
        if offset > size:
            return Response({"status": 301}, status=status.HTTP_400_BAD_REQUEST)
        elif offset + self.LIMIT < size:
            barbers = queryset[offset: offset + self.LIMIT]
        else:
            barbers = queryset[offset:]
        barbers = self.serializer_class(barbers, many=True,
                                        context={"user_location": customer_location.location})
        return Response(barbers.data)


class SearchBarbers(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Barber.objects.all()
    serializer_class = BarberRecordSerializer

    def post(self, request):
        """
        Filter barbers based on price range and services
        :param request:
        :return:
        """
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        customer_location = customer.location.filter(chosen=True).first()
        data = request.data
        try:
            serviceID, price_lower_limit, price_upper_limit = data['serviceID'], data['price_lower_limit'], data[
                'price_upper_limit']
        except:
            return Response({"status": 306}, status=status.HTTP_400_BAD_REQUEST)
        barbers = []
        for barber in self.queryset.all():
            services = barber.services.filter(service__serviceId__in=serviceID)
            if not services:
                continue
            price = services.aggregate(Sum('cost'))['cost__sum']
            if price_lower_limit <= price <= price_upper_limit:
                barbers.append(barber)
        queryset = sorted(barbers,
                          key=lambda barber: ClosestBarbers.cal_dist(customer_location.location, barber.location))
        barbers = self.serializer_class(queryset, many=True, context={"user_location": customer_location.location})
        return Response(barbers.data)

    def get(self, request):
        """
        Search barbers with parameter search field
        :param request:
        :return:
        """
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        customer_location = customer.location.filter(chosen=True).first()

        barber_name = request.GET.get('barber_name')
        if not barber_name:
            return Response({"status": 306}, status=status.HTTP_400_BAD_REQUEST)
        barbers = self.queryset.filter(Q(barberName__icontains=barber_name) | Q(firstName__icontains=barber_name) | Q(
            lastName__icontains=barber_name))
        barbers = sorted(barbers,
                         key=lambda barber: ClosestBarbers.cal_dist(customer_location.location, barber.location))
        barbers = self.serializer_class(barbers, many=True, context={"user_location": customer_location.location})
        return Response(barbers.data)


class CustomerLocationHandler(APIView):
    """
    Location handler for customer
    adds functionality as below:
        - get customer locations
        - change customer chosen location
        - adds a new location to customer
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
    queryset = Location.objects.all()

    class Action:
        GET = 0
        CHANGE = 1

    def post(self, request):
        """
        Add location to customer locations
        :param request:
        :return:
        """
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(data=
                                           {"location": data['location'], "address": data['address'],
                                            "customerID": customer.customer_id})
        if not serializer.is_valid():
            return Response({"status": 303}, status=status.HTTP_400_BAD_REQUEST)
        location = serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        """
        Change chosen location for customer
        :param request:
        :return:
        """
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response({"status": 302}, status=status.HTTP_404_NOT_FOUND)
        action = request.GET.get('action')
        if not action:
            action = self.Action.GET
        action = int(action)
        if action == self.Action.GET:
            return self.get_customer_locations(customer)
        elif action == self.Action.CHANGE:
            return self.change_customer_chose_location(customer, request)
        return Response()

    def get_customer_locations(self, customer):
        locations = self.queryset.filter(customer=customer)
        serializer = self.serializer_class(locations, many=True)
        return Response(serializer.data)

    def change_customer_chose_location(self, customer, request):
        lid = request.GET.get('id')
        if not lid:
            return Response({"status": 305}, status=status.HTTP_400_BAD_REQUEST)
        lid = lid
        location = self.queryset.filter(customer=customer, chosen=True)
        if location:
            for l in location:
                l.chosen = False
                l.save()
        location = self.queryset.filter(customer=customer, ID=lid).first()
        if not location:
            return Response({"status": 305}, status=status.HTTP_400_BAD_REQUEST)
        location.chosen = True
        location.save()
        return Response()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_locations(request):
    try:
        user = request.user
        customer = Customer.objects.filter(user=user).first()
        if not customer:
            return Response({"status": 305}, status=status.HTTP_400_BAD_REQUEST)
        locations = LocationSerializer(customer.location.all(), many=True)
        return Response(locations.data)
    except:
        return Response({"status": 310}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
