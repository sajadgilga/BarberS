from rest_framework import serializers

from client.models import Customer, Barber, Comment, ServiceSchema, PresentedService, Service
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['firstName', 'lastName', 'snn', 'gender', 'credit', 'location']
        # phone deleted !!!!!!!!!!!

        def create(self,validated_data):
            return Customer(**validated_data)
        def update(self,instance,validated_data):
            instance.firstname = validated_data.get('firstname',instance.firstname)
            instance.lastname = validated_data.get('lastname',instance.lastname)
            instance.snn = validated_data.get('snn',instance.snn)
            instance.gender = validated_data.get('gender',instance.gender)
            instance.location = validated_data.get('location',instance.location)
            instance.image = validated_data.get('image',instance.image)
            instance.save()
            return instance
#         the fields had changed !!!!!!1


class BarberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barber
        fields = ['firstName', 'lastName', 'snn', 'phone', 'gender', 'address', 'point', 'location']


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

