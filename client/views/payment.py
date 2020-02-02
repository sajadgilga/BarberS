import datetime

from django.http import HttpResponse, JsonResponse
from rest_framework import status
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

    def post(self, request):
        payment = 0
        user = request.user
        if user is None:
            return Response({"status": 500}, status=status.HTTP_400_BAD_REQUEST)
        customer = Customer.objects.filter(phone=user.username).first()  # customer not exists
        if customer is None:
            return Response({"status": 502}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            data['customer_id'] = customer.customer_id
            serializer = PresentedServiceSerializer_in(data=data)
        except Exception as error:
            return Response({"status": 502} + error, status=status.HTTP_400_BAD_REQUEST)  # invalid data
        if serializer.is_valid():
            barber_id = serializer.validated_data['barber']['barber_id']

            service_id_list = serializer.validated_data['service_id_list']  # todo: serviceId must change to service_id
        else:
            return Response({"status": 503}, status=status.HTTP_400_BAD_REQUEST)
        barber = Barber.objects.filter(barber_id=barber_id).first()
        if barber is None:
            return Response({"status": 500},
                            status=status.HTTP_400_BAD_REQUEST)  # there is no barber with this username


        temp_presentService_status = 1 # 1 is the key for value UNVERIFIED




        temp_presentService = serializer.create(validated_data=serializer.validated_data, barber=barber,
                                                status=temp_presentService_status,
                                                customer=customer)
        for service_id in service_id_list:
            service = Service.objects.filter(service_id=service_id).first()

            if service is None:
                return Response({"status": 500},
                                status=status.HTTP_400_BAD_REQUEST)  # this service not exists for barber
            payment = payment + service.cost
            temp_presentService.service.add(service)
        if self.check_reserve(temp_presentService, barber):
            return Response({"status": 200, "payment": payment}, status=status.HTTP_200_OK)
            # todo: payment request does not send to the port !

            # result = client.service.PaymentRequest(MERCHANT=settings.MERCHANT, amount=settings.amount,
            #                                        description=settings.description,
            #                                        email=settings.email,
            #                                        mobile=settings.email, CallbackURL=settings.CallbackURL)
            # temp_presentService.authority = result.Authority
            # if result.Status == 100:
            #     return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
            # else:
            #     return HttpResponse('Error code: ' + str(result.Status))
            # PresentedService.objects.filter(temp_presentService).delete()
        else:
            PresentedService.objects.filter(id=temp_presentService.id).delete()
            return Response({"status": 502}, status=status.HTTP_400_BAD_REQUEST)

    def check_reserve(self, presnted_service, barber):
        week_day = presnted_service.reserveTime.date().weekday()
        work_day = WorkDay.objects.filter(barber=barber).first()
        if work_day.week_days[week_day] is "0":
            return False
        date = presnted_service.reserveTime.date()
        if PresentedService.objects.filter(shift=presnted_service.shift).count()-1 is 0:
            return False
        cnt = PresentedService.objects.filter(reserveTime__day=date.day, reserveTime__month=date.month,
                                              reserveTime__year=date.year,
                                              barber=barber,
                                              shift=presnted_service.shift).count() - 1  # minus one because this presented service is saved !
        if self.shift_limit_verification(cnt, settings.MAX_RESERVE_LIMIT):
            return False
        if presnted_service.reserveTime.date() < datetime.date.today():  # todo : time checking with day
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

# 500 not exist
# 501 not allowed (profiled must complete)
# 502 bad input like post method with wrong body !
# 503 not validated data
