import json
from random import randint

from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from client.models import Barber, Customer
from client.serializers import BarberSerializer, BarberRecordSerializer


class BestBarbers(APIView):
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

