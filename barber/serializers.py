from rest_framework.serializers import ModelSerializer

from client.models import PresentedService


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = PresentedService
        fields = ['project_id', 'customer_name', 'customer_id', 'location', 'reserveTime', 'services']
