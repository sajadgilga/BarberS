from django.contrib.gis.geos import Point
from django.db.models import Q, Sum
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS.settings import error_status
from BarberS.utils import get_error_obj
from client.models import Barber, Customer, Location, AppSettings
from client.serializers import BarberRecordSerializer
from client.serializers import LocationSerializer


class SampleLocation:
    long = None
    lat = None

    def __init__(self, long, lat):
        self.long = long
        self.lat = lat


@api_view(['GET'])
@permission_classes([AllowAny])
def get_configs(request):
    return Response({"error_map": error_status})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_home_page(request):
    user = request.user
    try:
        customer = Customer.objects.get(user=user)
    except:
        return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
    long, lat = request.GET.get('long'), request.GET.get('lat')
    user_location = SampleLocation(long, lat)
    if not long or not lat:
        user_location = customer.location.filter(chosen=True).first()

    closest_data, err = ClosestBarbers.closest(0, ClosestBarbers.LIMIT, Barber.objects.all(), user_location,
                                               BarberRecordSerializer, customer)
    if err == 1:
        return Response(closest_data, status=status.HTTP_400_BAD_REQUEST)
    best_data, err = BestBarbers.best(0, BestBarbers.LIMIT, Barber.objects.all().order_by('-point'), user_location,
                                      BarberRecordSerializer, customer)
    if err == 1:
        return Response(best_data, status=status.HTTP_400_BAD_REQUEST)
    return Response({"best_barbers": best_data.data, "closest_barbers": closest_data.data})


class BestBarbers(APIView):
    """
    API to get best barbers according to their points
    """
    permission_classes = [IsAuthenticated]
    queryset = Barber.objects.all().order_by('-point')
    serializer_class = BarberRecordSerializer
    LIMIT = 10

    @staticmethod
    def best(offset, limit, dataset, user_location, serializer_class, customer):
        offset = limit * int(offset)
        size = dataset.count()
        if offset > size:
            return 301, 1
        elif offset + limit < size:
            barbers = dataset[offset: offset + limit]
        else:
            barbers = dataset[offset:]
        if not user_location:
            return get_error_obj('no_location_found'), 1
        barbers = serializer_class(barbers, many=True,
                                   context={"user_location": user_location, 'customer': customer})
        return barbers, 0

    def get(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
        offset = request.GET.get('offset')
        if not offset:
            offset = 0
        long, lat = request.GET.get('long'), request.GET.get('lat')
        user_location = SampleLocation(long, lat)
        if not long or not lat:
            user_location = customer.location.filter(chosen=True).first()

        appSettings = AppSettings.load()
        self.queryset = self.queryset.exclude(Q(isTopBarber=-1) | Q(point__lte=appSettings.threshold))
        barbers_data, err = BestBarbers.best(offset, self.LIMIT, self.queryset, user_location, self.serializer_class, customer)
        if err == 1:
            return Response(barbers_data, status=status.HTTP_400_BAD_REQUEST)
        return Response(barbers_data.data)


class ClosestBarbers(APIView):
    """
    API to get closest barbers to customer
    """
    permission_classes = [IsAuthenticated]
    queryset = Barber.objects.all()
    serializer_class = BarberRecordSerializer
    LIMIT = 10

    @staticmethod
    def closest(offset, limit, dataset, user_location, serializer_class, customer):
        if not user_location:
            return get_error_obj('no_location_found'), 1
        queryset = sorted(dataset.all(),
                          key=lambda barber: ClosestBarbers.cal_dist(user_location,
                                                                     [barber.long, barber.lat]))

        offset = limit * int(offset)
        size = dataset.count()
        if offset > size:
            return 301, 1
        elif offset + limit < size:
            barbers = queryset[offset: offset + limit]
        else:
            barbers = queryset[offset:]
        barbers = serializer_class(barbers, many=True,
                                   context={
                                       "user_location": user_location, 'customer': customer})
        return barbers, 0

    @staticmethod
    def cal_dist(user_location, barber_location):
        # if user_location == '' or barber_location == '':
        #     return -1
        # [user_long, user_lat] = user_location.split(LOCATION_SEPARATOR)
        # [barber_long, barber_lat] = barber_location.split(LOCATION_SEPARATOR)
        try:
            [user_long, user_lat] = [user_location.long, user_location.lat]
            [barber_long, barber_lat] = barber_location
            p1 = Point(float(user_long), float(user_lat))
            p2 = Point(float(barber_long), float(barber_lat))
            d = p1.distance(p2)
            return d * 10 ** 5
        except:
            return -1

    def get(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(user=user)
        except:
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
        offset = request.GET.get('offset')
        if not offset:
            offset = 0
        long, lat = request.GET.get('long'), request.GET.get('lat')
        user_location = SampleLocation(long, lat)
        if not long or not lat:
            user_location = customer.location.filter(chosen=True).first()
        barbers_data, err = ClosestBarbers.closest(offset, self.LIMIT, self.queryset, user_location,
                                                   self.serializer_class, customer)
        if err == 1:
            return Response(barbers_data, status=status.HTTP_400_BAD_REQUEST)
        return Response(barbers_data.data)


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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
        long, lat = request.GET.get('long'), request.GET.get('lat')
        user_location = SampleLocation(long, lat)
        if not long or not lat:
            user_location = customer.location.filter(chosen=True).first()
        if not user_location:
            return Response(get_error_obj('no_location_found'), status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        try:
            serviceID, price_lower_limit, price_upper_limit = data['serviceID'], data['price_lower_limit'], data[
                'price_upper_limit']
        except:
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
        barbers = []
        for barber in self.queryset.all():
            services = barber.services.filter(service_id__in=serviceID)
            if not services:
                continue
            price = services.aggregate(Sum('cost'))['cost__sum']
            if price_lower_limit <= price <= price_upper_limit:
                barbers.append(barber)
        queryset = sorted(barbers,
                          key=lambda barber: ClosestBarbers.cal_dist(user_location,
                                                                     [barber.long, barber.lat]))
        barbers = self.serializer_class(queryset, many=True, context={
            "user_location": user_location, 'customer': customer})
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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)

        long, lat = request.GET.get('long'), request.GET.get('lat')
        user_location = SampleLocation(long, lat)
        if not long or not lat:
            user_location = customer.location.filter(chosen=True).first()
        if not user_location:
            return Response(get_error_obj('no_location_found'), status=status.HTTP_400_BAD_REQUEST)

        barber_name = request.GET.get('barber_name')
        if not barber_name:
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
        barbers = self.queryset.filter(Q(barberName__icontains=barber_name) | Q(firstName__icontains=barber_name) | Q(
            lastName__icontains=barber_name) | Q(name__icontains=barber_name))
        barbers = sorted(barbers,
                         key=lambda barber: ClosestBarbers.cal_dist(user_location,
                                                                    [barber.long, barber.lat]))
        barbers = self.serializer_class(barbers, many=True, context={
            "user_location": user_location, 'customer': customer})
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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(data=
                                           {"long": data['long'], "lat": data['lat'], "address": data['address'],
                                            "customerID": customer.customer_id})
        if not serializer.is_valid():
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_404_NOT_FOUND)
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
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
        lid = lid
        location = self.queryset.filter(customer=customer, chosen=True)
        if location:
            for l in location:
                l.chosen = False
                l.save()
        location = self.queryset.filter(customer=customer, ID=lid).first()
        if not location:
            return Response(get_error_obj('no_location_found'), status=status.HTTP_400_BAD_REQUEST)
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
            return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
        locations = LocationSerializer(customer.location.all(), many=True)
        return Response(locations.data)
    except:
        return Response(get_error_obj('server_error'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
