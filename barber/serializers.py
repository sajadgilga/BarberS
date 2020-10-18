from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from BarberS.settings import SERVER_BASE_URL, generate_image_url
from client.models import PresentedService, Service


class ServiceSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.schema.name

    class Meta:
        model = Service
        fields = ['name', 'service_id']


class ProjectSerializer(ModelSerializer):
    customer_id = serializers.CharField(source='customer.customer_id')
    customer_name = serializers.SerializerMethodField()
    customer_image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    services = ServiceSerializer(many=True, read_only=True)

    def get_location(self, obj):
        pass

    def get_customer_name(self, obj):
        return '{} {}'.format(obj.customer.firstName, obj.customer.lastName)

    def get_customer_image(self, obj):
        try:
            return generate_image_url(obj.customer)
        except:
            return ''

    class Meta:
        model = PresentedService
        fields = ['project_id', 'customer_name', 'customer_image', 'customer_id', 'location', 'reserveTime',
                  'services']
