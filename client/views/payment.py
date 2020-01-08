import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect

from BarberS import settings
from client.serializers import *
from client.models import Barber, Customer, PresentedService, WorkDay
from zeep import Client as client


class PaymentRequest(APIView):
    permission_classes = [IsAuthenticated]
    payment = 0

    def post(self, request):

        user = request.user
        if user is None:
            return Response({"status": 500}, status=status.HTTP_400_BAD_REQUEST)
        customer = Customer.objects.filter(phone=user.username).first()  # customer not exists
        if customer is None:
            return Response({"status": 502}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = PresentedServiceSerializer(request.data, context={'customer_ID', customer.ID})
        except Exception as error:
            return Response({"status": 502} + error, status=status.HTTP_400_BAD_REQUEST)  # invalid data
        if serializer.is_valid():
            barber_username = serializer.validated_data['barber_username']
            serviceID_list = serializer.validated_data[' serviceID_list ']
        barber = Barber.objects.filter(user__username=barber_username).first()
        if barber is None:
            return Response({"status": 500},
                            status=status.HTTP_400_BAD_REQUEST)  # there is no barber with this username
        temp_presentService = serializer.create(validated_data=serializer.validated_data)
        for id in serviceID_list:
            service = Service.objects.filter(service__serviceId=id).first()
            if service is None:
                return Response({"status": 500},
                                status=status.HTTP_400_BAD_REQUEST)  # this service not exists for barber
            # payment =payment+ service.cost
            temp_presentService.service.add(service)
        if self.check_reserve(temp_presentService, barber):
            result = client.service.PaymentRequest(MERCHANT=settings.MERCHANT, amount=settings.amount,
                                                   description=settings.description,
                                                   email=settings.email,
                                                   mobile=settings.email, CallbackURL=settings.CallbackURL)
            temp_presentService.authority = result.Authority
            if result.Status == 100:
                return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
            else:
                return HttpResponse('Error code: ' + str(result.Status))
            PresentedService.objects.filter(temp_presentService).delete()
        else:
            return Response({"status": 503}, status=status.HTTP_400_BAD_REQUEST)
            PresentedService.objects.filter(temp_presentService).delete()

    def check_reserve(self, presnted_service, barber):
        week_day = presnted_service.reserveTime.date().weekday()
        work_day = WorkDay.objects.filter(barber=barber).first()
        if work_day.week_days[week_day] is "0":
            return False
        cnt = PresentedService.objects.filter(reserveTime=presnted_service.reserveTime, barber=barber,
                                              shift=presnted_service.shift).count() - 1  # minus one because this presented service is saved !
        if self.shift_limit_verification(cnt, settings.MAX_RESERVE_LIMIT):
            return False
        if presnted_service.reserveTime < datetime.datetime.now():  # todo : time checking with day
            return False
        return True

    def shift_limit_verification(self, cnt, limit):
        return cnt > limit

        # result = client.service.PaymentRequest(settings.PAYMENT_AMOUNT,
        #                                        settings.MERCHANT,
        #                                        settings.PAYMENT_DESCRIPTION,
        #                                        settings.PAYMENT_EMAIL,
        #                                        settings.PAYMENT_MOBILE,
        #                                        settings.PAYMENT_CallbackURL
        #                                        )
        #
        # def send_request(request):
        #     client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')  # address has to be changed !
        #     result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
        #     if result.Status == 100:
        #         return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
        #     else:
        #         return HttpResponse('Error code: ' + str(result.Status))


def verify(self, request):
    result = client.service.PaymentVerification(settings.MERCHANT, request.GET['Authority'], settings.amount)
    authority = request.GET('Authority')  # todo : define authority for presentedService
    presented_service = PresentedService.objects.filter(authority=authority)
    if request.GET.get('Status') == 'OK':
        if result.Status == 100:
            # find presented_service  with authoirty
            return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))

        elif result.Status == 101:
            # what is the deffrent of 101 and 100 status?
            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            PresentedService.objects.filter(presented_service).delete()
            return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
    else:
        PresentedService.objects.filter(presented_service).delete()
        return HttpResponse('Transaction failed or canceled by user')

# 500 not exists
# 502 invalid input
