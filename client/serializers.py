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
    customerID = serializers.CharField(source='customer.ID')

    class Meta:
        model = Location
        fields = ['location', 'address', 'customerID', 'ID']
        read_only_fields = ['ID']

    def create(self, validated_data):
        customer = Customer.objects.filter(ID=validated_data.pop('customer')['ID']).first()
        location = Location(**validated_data)
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
    id = serializers.CharField(source='user.username')
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
    class Meta:
        model = Comment
        fields = ['customer', 'barber', 'created_time', 'text']


class ServiceSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSchema
        fields = ['name', 'serviceId', 'description', ]


class PresentedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentedService
        fields = ['barber', 'customer', 'service', 'reserveTime', 'creationTime', 'status', 'payment', 'shift', ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['barber', 'service', 'cost']

class BarberSerializer_out(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ['firstName', 'lastName',  'gender', 'address', 'point', 'location','image']

class CustomerSerializer_out(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields =['firstName', 'lastName', 'snn', 'phone', 'gender', 'location','image','like']
#         how to add like ?

