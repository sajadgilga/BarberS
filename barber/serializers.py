from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from BarberS.settings import generate_image_url
from client.models import PresentedService, Service, ServiceSchema


class ServiceSchemaSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    def get_icon(self, obj):
        try:
            image_path = obj.icon.storage.base_url + obj.icon.storage.base_location + '/' + obj.icon.name
            parts = image_path.split('http://')
            if len(parts) == 3:
                image_path = obj.icon.storage.base_url + '/' + obj.icon.name
            if 'static/images' not in image_path:
                image_path = obj.icon.storage.base_url + '/static/images/services/' + obj.icon.name
            return image_path
        except:
            return ''

    class Meta:
        model = ServiceSchema
        fields = ['name', 'service_schema_id', 'description', 'icon', 'lower_limit', 'upper_limit']


class ServiceSerializer(ModelSerializer):
    name = serializers.SerializerMethodField()
    schema = ServiceSchemaSerializer()

    def get_name(self, obj):
        return obj.schema.name

    class Meta:
        model = Service
        fields = ['name', 'service_id', 'schema', 'cost']


class ProjectSerializer(ModelSerializer):
    customer_id = serializers.CharField(source='customer.customer_id')
    customer_name = serializers.SerializerMethodField()
    customer_image = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    services = ServiceSerializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()

    def get_location(self, obj):
        pass

    def get_customer_name(self, obj):
        return '{} {}'.format(obj.customer.firstName, obj.customer.lastName)

    def get_customer_image(self, obj):
        try:
            return generate_image_url(obj.customer, img_type='customers')
        except:
            return ''

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = PresentedService
        fields = ['project_id', 'customer_name', 'customer_image', 'customer_id', 'location', 'reserveTime',
                  'services', 'status']
