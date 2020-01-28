from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User, AnonymousUser
from client.models import *
from client.serializers import *
import json
from rest_framework.renderers import JSONRenderer
import io
from rest_framework.parsers import JSONParser


@api_view(['GET'])
def get_comment(request):
    limit = 5
    offset = request.GET.get('offset')
    if not offset:
        offset = 0
    offset = limit * int(offset)
    if offset < 0:
        return Response({"status": 804}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user is AnonymousUser:
        return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 802}, status=status.HTTP_404_NOT_FOUND)
    if barber.is_verified is False:
        return Response({"status": 801}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        queryset = Comment.objects.filter(barber=barber).order_by('created_time')
    except:
        return Response({"status": 802}, status=status.HTTP_404_NOT_FOUND)
    size = queryset.count()
    if offset > size:
        return Response({"status": 804}, status=status.HTTP_400_BAD_REQUEST)
    elif offset + limit < size:
        comment = queryset[offset: offset + limit]
    else:
        comment = queryset[offset:]
    serializer = CommentSerializer(comment, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# todo : need api for verify barber
@permission_classes(['IsAuthenticated'])
@api_view(['GET'])
def get_profile(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 802}, status=status.HTTP_400_BAD_REQUEST)
    serializer = bar_BarberSerializer(barber)

    return Response(serializer.data)


class Get_home(APIView):
    LIMIT = 5
    stat = ['new', 'done', 'not paid']  # statuses !

    def get(self, request):
        stat = self.stat
        length = len(stat)
        offset = [0 for i in range(length)]
        queryset = [[] for i in range(length)]
        serializer = [[] for i in range(length)]
        final = []
        # final = json.dumps(final)
        try:
            user = request.user
            if user is AnonymousUser or None:
                return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)
            barber = Barber.objects.filter(user=user).first()
            if barber is None:
                return Response({"status": 802}, status=status.HTTP_400_BAD_REQUEST)
            if barber.is_verified is False:
                return Response({"status": 801}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            for i in range(length):
                temp = PresentedService.objects.filter(status=stat[i])
                queryset[i] = temp

            for i in range(length):
                offset[i] = request.GET.get('offset{}'.format(i + 1))

            for i in range(length):
                queryset[i] = self.manage_set(offset[i], queryset[i])
                if queryset[i] is None:
                    return Response({"status": 804}, status=status.HTTP_400_BAD_REQUEST)

            for i in range(length):
                serializer[i] = PresentedServiceSerializer(queryset[i], many=True)
            cnt = 0
            for i in serializer:
                temp = {}
                temp[stat[cnt]] = i.data
                json = JSONRenderer().render(temp)
                stream = io.BytesIO(json)
                data = JSONParser().parse(stream)
                final.append(data)
                cnt += 1
        except Exception as error:
            return Response({"status": 805}, status=status.HTTP_400_BAD_REQUEST)

        return Response(final)

    def post(self, request):
        pass

    def manage_set(self, offset, queryset):
        if not offset or offset is None:
            offset = 0
        offset = self.LIMIT * int(offset)
        if offset < 0:
            offset = self.LIMIT * int(offset)
        size = queryset.count()
        if offset > size:
            return None
        elif offset + self.LIMIT < size:
            set = queryset[offset: offset + self.LIMIT]
        else:
            set = queryset[offset:]

        return set


@api_view(['POST'])
def add_samples(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 802}, status=status.HTTP_400_BAD_REQUEST)
    if barber.is_verified is False:
        return Response({"status": 801}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    data = request.data
    data['barber_id'] = barber.barber_id
    serializer = SampleWorkSerializer_in(data=data)
    if serializer.is_valid() is False:
        return Response({"status": 807}, status=status.HTTP_400_BAD_REQUEST)
    sample = serializer.create(serializer.validated_data)
    if sample is None:
        return Response({"status": 806}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_profile(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 802}, status=status.HTTP_400_BAD_REQUEST)

    serializer = BarberSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"status": 807}, status=status.HTTP_400_BAD_REQUEST)
    temp = serializer.update(barber, serializer.validated_data)
    if temp is None:
        return Response({"status": 806}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
def shift_handler(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 803}, status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 802}, status=status.HTTP_400_BAD_REQUEST)
    if barber.is_verified is False:
        return Response({"status": 801}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    data['barber_id'] = barber.barber_id
    serializer = ShiftSerializer(data=data)
    if serializer.is_valid() is False:
        return Response({"status": 807}, status=status.HTTP_400_BAD_REQUEST)
    shift = serializer.create(serializer.validated_data)
    if shift is None:
        return Response({"status": 806}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"status": 200}, status=status.HTTP_200_OK)

# 801 : barber not verified
# 802 : barber not exist
# 803 : Anonymous User
# 804 : wrong offset
# 805 : bad input (general) for try except
# 806 : instance can not be create or update
# 807 : serializer is not valid (bad input)
