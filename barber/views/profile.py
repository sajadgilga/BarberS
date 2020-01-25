from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User, AnonymousUser
from client.models import *
from client.serializers import *


@api_view(['GET'])
def get_comment(request):
    limit = 5
    offset = request.GET.get('offset')
    if not offset:
        offset = 0
    offset = limit * int(offset)
    if offset < 0:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user is AnonymousUser:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_404_NOT_FOUND)
    if barber.is_verified is False:
        return Response({"status": 401}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    try:
        queryset = Comment.objects.filter(barber=barber).order_by('created_time')
    except:
        return Response({"status": 400}, status=status.HTTP_404_NOT_FOUND)
    size = queryset.count()
    if offset > size:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    serializer = bar_BarberSerializer(barber)

    return Response(serializer.data)


class Get_home(APIView):
    LIMIT = 5
    status = ['done', 'new', 'undone']

    def get(self, request):
        offset, queryset, serializer = [i for i in range(status)]
        final = []
        try:
            user = request.user
            if user is AnonymousUser or None:
                return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
            barber = Barber.objects.filter(user=user).first()
            if barber is None:
                return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
            if barber.is_verified is False:
                return Response({})

            for i in range(len(status)):
                queryset[i] = PresentedService.objects.filter(status=status[i])

                for i in range(len(status)):
                    offset[i] = request.GET.get('offset{}'.format(i))

            for i in range(len(status)):
                queryset[i] = self.manage_set(self, offset[i], queryset[i])

            for i in range(len(status)):
                serializer[i] = PresentedServiceSerializer(queryset[i], many=True)

            for i in serializer:
                final = final + status[i] + ':' + i.data + ' '
        except:
            return Response({})  ##################################################fill this line!

        return Response(final, status=status.HTTP_200_OK)

    def manage_set(self, offset, queryset):
        if not offset:
            offset = 0
        if offset < 0:
            offset = self.LIMIT * int(offset)
        size = queryset.count()
        if offset > size:
            return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
        elif offset + self.LIMIT < size:
            set = queryset[offset: offset + self.LIMIT]
        else:
            set = queryset[offset:]

        return set

@api_view(['POST'])
def add_samples(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    if barber.is_verified is False:
        return Response({})
    data = request.data
    data['barber_id']:barber.barber_id
    serializer = SampleWorkSerializer_in(data = data)
    if serializer.is_valid() is False:
        return Response(serializer.errors)
    sample = serializer.create(serializer.validated_data)
    if sample is None:
        return Response({"it is None"})
    return Response({'status': 200}, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_profile(request):
    user = request.user
    if user is AnonymousUser or None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    barber = Barber.objects.filter(user=user).first()
    if barber is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)

    serializer = BarberSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    temp = serializer.update(barber, serializer.validated_data)
    if temp is None:
        return Response({"status": 400}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'status': 200}, status=status.HTTP_200_OK)
