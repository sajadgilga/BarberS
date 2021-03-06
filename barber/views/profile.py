from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS.utils import get_error_obj
from client.serializers import *


@api_view(['GET'])
def get_comment(request):
    limit = 5
    offset = request.GET.get('offset')
    if not offset:
        offset = 0
    offset = limit * int(offset)
    if offset < 0:
        return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user is AnonymousUser:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
    if barber.is_verified is False:
        return Response(get_error_obj('access_denied'), status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        queryset = Comment.objects.filter(barber=barber).order_by('created_time')
    except:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
    size = queryset.count()
    if offset > size:
        return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
    elif offset + limit < size:
        comment = queryset[offset: offset + limit]
    else:
        comment = queryset[offset:]
    serializer = bar_CommentSerializer(comment, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# todo : need api for verify barber
@permission_classes(['IsAuthenticated'])
@api_view(['GET'])
def get_profile(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
    serializer = BarberSerializer_out(barber)
    # serializer = bar_BarberSerializer(barber)

    return Response(serializer.data)


class Get_home(APIView):
    LIMIT = 5
    stat = [1, 2, 3]  # statuses !

    def get(self, request):
        stat = PresentedService.STATUS
        length = len(stat)
        # offset = [0 for i in range(length)]
        queryset = [[] for i in range(length)]
        serializer = [[] for i in range(length)]
        final = {}
        # final = json.dumps(final)
        try:
            user = request.user
            if user is AnonymousUser or None:
                return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
            barber = Barber.objects.filter(user=user).first()
            if barber is None:
                return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
            if barber.is_verified is False:
                return Response(get_error_obj('access_denied'), status=status.HTTP_405_METHOD_NOT_ALLOWED)

            for i in range(length):
                queryset[i] = PresentedService.objects.filter(status=stat[i][0])

                # for i in range(length):
                #     offset[i] = request.GET.get('offset{}'.format(i + 1))
                #
                # for i in range(length):
                #     queryset[i] = self.manage_set(offset[i], queryset[i])
                if queryset[i] is None:
                    queryset[i] = []

            #         return Response({"status": 804}, status=status.HTTP_400_BAD_REQUEST)

            for i in range(length):
                serializer[i] = PresentedServiceSerializer_home(queryset[i], many=True)
            cnt = 0
            # extrat_data = {'barber': barber.barberName, 'name': barber.firstName + ' ' + barber.lastName}
            for i in serializer:
                final[stat[cnt][1]] = i.data
                # temp = {}
                # temp[stat[cnt][1]] = i.data
                # json = JSONRenderer().render(temp)
                # stream = io.BytesIO(json)
                # data = JSONParser().parse(stream)
                # final.append(data)
                cnt += 1
        except Exception as error:
            return Response(get_error_obj('server_error'), status=status.HTTP_400_BAD_REQUEST)

        return Response(final)

    def post(self, request):
        pass

    # def manage_set(self, offset, queryset):
    #     if not offset or offset is None:
    #         offset = 0
    #     offset = self.LIMIT * int(offset)
    #     if offset < 0:
    #         offset = self.LIMIT * int(offset)
    #     size = queryset.count()
    #     if offset > size:
    #         return None
    #     elif offset + self.LIMIT < size:
    #         set = queryset[offset: offset + self.LIMIT]
    #     else:
    #         set = queryset[offset:]
    #
    #     return set


@api_view(['POST'])
def add_samples(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
    if barber.is_verified is False:
        return Response(get_error_obj('access_denied'), status=status.HTTP_405_METHOD_NOT_ALLOWED)
    data = request.data
    data['barber_id'] = barber.barber_id
    serializer = SampleWorkSerializer_in(data=data)
    if serializer.is_valid() is False:
        return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
    sample = serializer.create(serializer.validated_data)
    if sample is None:
        return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_profile(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)

    serializer = BarberSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
    temp = serializer.update(barber, serializer.validated_data)
    if temp is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
def shift_handler(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
    if barber.is_verified is False:
        return Response(get_error_obj('access_denied'), status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    data['barber_id'] = barber.barber_id
    serializer = ShiftSerializer(data=data)
    if serializer.is_valid() is False:
        return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
    shift = serializer.create(serializer.validated_data)
    if shift is None:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": 200}, status=status.HTTP_200_OK)


class BarberLocationHandler(APIView):
    """
    Location handler for customer
    adds functionality as below:
        - get customer locations
        - change customer chosen location
        - adds a new location to customer
    """
    permission_classes = [IsAuthenticated]

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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(data=
                                           {"long": data['long'], "lat": data['lat'], "address": data['address'],
                                            "customerID": customer.customer_id})
        if not serializer.is_valid():
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
        location = serializer.create(serializer.validated_data)
        return Response(status=status.HTTP_200_OK)

# 801 : barber not verified
# 802 : barber not exist
# 803 : Anonymous User
# 804 : wrong offset
# 805 : bad input (general) for try except
# 806 : instance can not be create or update
# 807 : serializer is not valid (bad input)
