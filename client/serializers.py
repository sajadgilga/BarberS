from rest_framework import serializers

from client.models import Customer, Barber, Comment, ServiceSchema, PresentedService, Service
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


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


# class CustomAuthSerializer(serializers.Serializer):
#     def update(self, instance, validated_data):
#         pass
#
#     def create(self, validated_data):
#         pass
#
#     phone = serializers.CharField(label=_("Phone"))
#     key_code = serializers.CharField(label=_("key_code"))
#
#     def validate(self, attrs):
#         phone = attrs.get('phone')
#         key_code = attrs.get('key_code')
#
#         if phone and :
#             user = authenticate(request=self.context.get('request'),
#                                 username=username, password=password)
#
#             # The authenticate call simply returns None for is_active=False
#             # users. (Assuming the default ModelBackend authentication
#             # backend.)
#             if not user:
#                 msg = _('Unable to log in with provided credentials.')
#                 raise serializers.ValidationError(msg, code='authorization')
#         else:
#             msg = _('Must include "username" and "password".')
#             raise serializers.ValidationError(msg, code='authorization')
#
#         attrs['user'] = user
#         return attrs
