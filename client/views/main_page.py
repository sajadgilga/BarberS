import json
from random import randint

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.db.models import F, ExpressionWrapper, CharField
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS.settings import LOCATION_SEPARATOR
from client.models import Barber, Customer
from client.serializers import BarberSerializer, BarberRecordSerializer


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
        barbers = self.serializer_class(barbers, many=True, context={"user_location": customer.location})
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
        queryset = sorted(self.queryset.all(), key=lambda barber: ClosestBarbers.cal_dist(customer.location, barber.location))

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
        barbers = self.serializer_class(barbers, many=True, context={"user_location": customer.location})
        return Response(barbers.data)
