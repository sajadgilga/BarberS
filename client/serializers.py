from django.contrib.gis.geos import Point
from rest_framework import serializers

from BarberS.settings import LOCATION_SEPARATOR
from client.models import Customer, Barber, Comment, ServiceSchema, PresentedService, Service, Location
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['firstName', 'lastName', 'snn', 'gender', 'credit']

        # phone deleted !!!!!!!!!!!

        def create(self, validated_data):
            return Customer(**validated_data)

        def update(self, instance, validated_data):
            instance.firstname = validated_data.get('firstname', instance.firstname)
            instance.lastname = validated_data.get('lastname', instance.lastname)
            instance.snn = validated_data.get('snn', instance.snn)
            instance.gender = validated_data.get('gender', instance.gender)
            instance.image = validated_data.get('image', instance.image)
            instance.save()
            return instance


class LocationSerializer(serializers.ModelSerializer):
    customerID = serializers.CharField(source='customer.customer_id')

    class Meta:
        model = Location
        fields = ['location', 'address', 'customerID', 'ID']
        read_only_fields = ['ID']

    def create(self, validated_data):
        customer = Customer.objects.filter(customer_id=validated_data.pop('customer')['customer_id']).first()
        location = Location(**validated_data, ID='location_{}'.format(Location.objects.count() + 1))
        location.customer = customer
        if len(customer.location.all()) == 0:
            location.chosen = True
        location.save()
        return location


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ['firstName', 'lastName', 'snn', 'phone', 'gender', 'address', 'point', 'location']


class BarberRecordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='barber_id')
    name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    def get_name(self, obj):
        return '{} {}'.format(obj.firstName, obj.lastName)

    def get_image_url(self, obj):
        try:
            return obj.image.url
        except:
            return ''

    def get_distance(self, obj):
        try:
            if self.context['user_location'] == '' or obj.location == '':
                return None
            [user_long, user_lat] = self.context['user_location'].split(LOCATION_SEPARATOR)
            [barber_long, barber_lat] = obj.location.split(LOCATION_SEPARATOR)
            p1 = Point(float(user_long), float(user_lat))
            p2 = Point(float(barber_long), float(barber_lat))
            d = p1.distance(p2)
            return d * 10 ** 5
        except:
            return None

    class Meta:
        model = Barber
        fields = ['id', 'name', 'image_url', 'distance']
        read_only_fields = ['id', 'name', 'image_url', 'distance']


class CommentSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField()
    barber_id = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['customer_id', 'barber_id', 'text']

    def create(self, validated_data):
        text = validated_data['text']
        try:
            customer = Customer.objects.filter(customer_id=validated_data['customer_id']).first()
        except Exception as error:
            return None
        try:
            barber = Barber.objects.filter(barber_id=validated_data['barber_id']).first()
        except Exception as error:
            return None
        comment = Comment.objects.create(customer=customer, barber=barber, text=text)
        comment.save()
        return comment


class ServiceSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSchema
        fields = ['name', 'serviceId', 'description', ]


class ServiceSchemaSerilzerIn(serializers.Serializer):
    serviceID_list = serializers.ListField(child=serializers.IntegerField())
    barber_username = serializers.CharField(max_length=150)


class PresentedServiceSerializer(serializers.ModelSerializer):
    barber_username = serializers.CharField(source='barber.user.username')
    customer_id = serializers.CharField(source='customer.customer_id')
    serviceId_list = serializers.SerializerMethodField()

    class Meta:
        model = PresentedService
        fields = ['barber_username', 'customer_id', 'serviceId_list', 'reserveTime', 'creationTime', 'status',
                  'payment',
                  'shift']

    def get_serviceId_list(self, obj):
        all = obj.service.all()
        try:
            l = []
            for i in all:
                id = i.service.serviceId
                l.append(id)
            return l
        except Exception as error:
            return error

    def create(self, validated_data, barber, customer):
        presented_service = PresentedService(customer=customer, barber=barber,
                                             reserveTime=validated_data['reservedTime'], shift=validated_data['shift'],
                                             status=validated_data['status'], payment=validated_data['payment'])
        presented_service.save()  # todo :depends on  implemention maybe you need to delete this
        return presented_service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['barber', 'service', 'cost']


class BarberSerializer_out(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ['firstName', 'lastName', 'gender', 'address', 'point', 'location', 'image','sample_list','barberName']


class CustomerSerializer_out(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['firstName', 'lastName', 'snn', 'phone', 'gender', 'location', 'image', 'like']
#         how to add like ?
