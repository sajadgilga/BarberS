import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS import settings
from client.serializers import *
from client.models import Barber, Customer, PresentedService, WorkDay


class PaymentRequest(APIView):
    permission_classes = [IsAuthenticated]

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
        barber = Barber.objects.filter(user__username=barber_username).first
        if barber is None:
            return Response({"status": 500},
                            status=status.HTTP_400_BAD_REQUEST)  # there is no barber with this username
        temp_presentService = serializer.create(validated_data=serializer.validated_data)
        for id in serviceID_list:
            service = Service.objects.filter(service__serviceId=id).first()
            if service is None:
                return Response({"status": 500},
                                status=status.HTTP_400_BAD_REQUEST)  # this service not exists for barber
            temp_presentService.service.add(service)
        if self.check_reserve(temp_presentService, barber):
            if self.check_payment():
                temp_presentService.save()
            else:
                return Response({"status": 503}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": 503}, status=status.HTTP_400_BAD_REQUEST)

    def check_reserve(self, presnted_service, barber):
        week_day = presnted_service.reserveTime.date().weekday()
        work_day = WorkDay.objects.filter(barber=barber).first()
        if work_day.week_days[week_day] is "0":
            return False
        cnt = PresentedService.objects.filter(reserveTime=presnted_service.reserveTime, barber=barber,
                                              shift=presnted_service.shift).count()
        if self.shift_limit_verification(cnt, settings.MAX_RESERVE_LIMIT):
            return False
        if presnted_service.reserveTime < datetime.datetime.now():  # todo : time checking with day
            return False
        return True

    def shift_limit_verification(self, cnt, limit):
        return cnt > limit

    def check_payment(self):
        pass
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

#
# class PaymentVerify(View):
#     def get(self, request):
#         client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
#         response = ''
#
#         if request.GET.get('Status') == 'OK':
#             result = client.service.PaymentVerification(settings.MERCHANT, request.GET['Authority'],
#                                                         settings.PAYMENT_AMOUNT)
#             if result.Status == 100:
#                 authority = request.GET['Authority']
#                 members = TeamMember.objects.filter(authority__contains=authority)
#                 team_name = members[0].registry_team_name
#
#                 new_user = User()
#                 new_user.username = team_name
#                 password = random_password()
#                 new_user.set_password(password)
#                 new_user.save()
#                 new_team = Team()
#                 new_team.user = new_user
#                 new_team.name = team_name
#                 new_team.save()
#                 for member in members:
#                     member.is_paid = True
#                     member.team = new_team
#                     member.save()
#
#                 mail_subject = 'تایید نهایی ثبت نام'
#                 html_content = render_to_string('account_details_mail.html',
#                                                 {'username': team_name, 'password': password})
#                 text_content = strip_tags(html_content)
#
#                 send_mail(
#                     mail_subject,
#                     text_content,
#                     EMAIL_HOST_USER,
#                     [members[0].email, members[1].email],
#                     fail_silently=False,
#                     html_message=html_content
#                 )
#
#                 for member in members:
#                     member.is_verify_mail_sent = True
#                     member.save()
#
#                 response = 'عملیات با موفقیت انجام شد ' + str(result.RefID)
#                 # return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
#             elif result.Status == 101:
#                 return HttpResponse('Transaction submitted : ' + str(result.Status))
#             else:
#                 response = 'عملیات پرداخت ناموفق بود' + str(result.Status)
#                 # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
#         else:
#             response = 'عملیات ناموفق بود یا توسط کاربر کنسل شد'
#             # return HttpResponse('Transaction failed or canceled by user')
#
#         return render(request, 'verify_payment.html', {'response': response})

# 500 not exists
# 502 invalid input
