from rest_framework import serializers

from client.models import Customer, Barber, Comment, ServiceSchema, PresentedService, Service


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['firstName', 'lastName', 'snn', 'phone', 'gender', 'like', 'credit', 'location']


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
