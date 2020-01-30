from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from barber.serializers import ProjectSerializer
from client.models import PresentedService, Service, Barber, ServiceSchema
from client.serializers import ServiceSchemaSerilzerIn, ServiceSchemaSerializer


class ServiceHandler(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()

    def create_or_update(self, request, service_id, barber):
        try:
            cost = request.data['cost']
        except:
            return Response({"status": 607}, status=status.HTTP_400_BAD_REQUEST)
        schema = ServiceSchema.objects.filter(service_schema_id=service_id).first()
        if schema.lower_limit is not 0 and schema.lower_limit > cost:
            return Response({"status": 608}, status=status.HTTP_409_CONFLICT)
        if schema.upper_limit is not -1 and schema.upper_limit < cost:
            return Response({"status": 608}, status=status.HTTP_409_CONFLICT)
        service = Service.objects.filter(schema__service_schema_id=service_id, barber=barber).first()
        if not service:
            service = Service(service_id="service_{}".format(Service.objects.count() + 1))
            service.barber = barber
            service.schema = schema
        service.cost = cost
        service.save()
        return Response()

    def delete(self, service_id, barber):
        service = Service.objects.filter(schema__service_schema_id=service_id, barber=barber).first()
        if not service:
            return Response({"status": 609}, status=status.HTTP_400_BAD_REQUEST)
        service.delete()
        return Response()

    def get(self, request):
        try:
            schemas = ServiceSchema.objects.all()
            schemas = ServiceSchemaSerializer(schemas, many=True)
            return Response(schemas.data)
        except:
            return Response({"status": 610}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # general problem

    def post(self, request):
        user = request.user
        try:
            barber = Barber.objects.filter(user=user).first()
        except:
            return Response({"status": 604}, status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response({"status": 600}, status=status.HTTP_401_UNAUTHORIZED)
        action = 1
        try:
            action = request.data['action']
        except:
            pass
        try:
            service_id = request.data['service_id']
        except:
            return Response({"status": 607}, status=status.HTTP_400_BAD_REQUEST)
        if action == 1:
            self.create_or_update(request, service_id, barber)
        elif action == 2:
            self.delete(service_id, barber)
        else:
            return Response({"status": 607}, status=status.HTTP_400_BAD_REQUEST)


class ProjectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PresentedService.objects.all().order_by('-creationTime')
    LIMIT = 10

    def get(self, request):
        user = request.user
        try:
            barber = Barber.objects.filter(user=user).first()
        except:
            return Response({"status": 604}, status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response({"status": 600}, status=status.HTTP_401_UNAUTHORIZED)
        project_status = request.GET.get('status')
        offset = request.GET.get('offset')
        if not offset:
            offset = 0
        if not project_status:
            return Response({"status": 605}, status=status.HTTP_400_BAD_REQUEST)
        if project_status == 'unverified':
            queryset = self.queryset.filter(status=PresentedService.STATUS[1])
        elif project_status == 'in_progress':
            queryset = self.queryset.filter(status=PresentedService.STATUS[3])
        else:
            queryset = self.queryset.filter(status=PresentedService.STATUS[4])
        size = queryset.count()
        if offset > size:
            return Response({"status": 606}, status=status.HTTP_400_BAD_REQUEST)
        elif offset + self.LIMIT < size:
            projects = queryset[offset: offset + self.LIMIT]
        else:
            projects = queryset[offset:]
        projects = ProjectSerializer(projects, many=True)
        return Response(projects.data)

    def post(self, request):
        user = request.user
        try:
            barber = Barber.objects.filter(user=user).first()
        except:
            return Response({"status": 604}, status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response({"status": 600}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            date = request.data['date']
            year, month, day = date.split('-')
            projects = self.queryset.filter(reserveTime__year=year, reserveTime__month=month, reserveTime__day=day)
            projects = ProjectSerializer(projects, many=True)
            return Response(projects.data)
        except:
            return Response({"status": 607}, status=status.HTTP_400_BAD_REQUEST)


class ProjectHandler(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PresentedService.objects.all()
    ACTIONS = ['verify', 'reject', 'end']

    def get(self, request, action):
        if action not in self.ACTIONS:
            return Response({"status": 601}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project_id = request.data['reserved_service_id']
        except:
            return Response({"status": 602}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        project = self.queryset.filter(project_id=project_id).first()
        if project.barber.user is not user:
            return Response({"status": 603}, status=status.HTTP_401_UNAUTHORIZED)
        if action == self.ACTIONS[0]:
            self.verify(project)
        elif action == self.ACTIONS[1]:
            self.reject(project)
        else:
            self.end(project)
        return Response()

    def verify(self, project):
        project.status = PresentedService.STATUS[3]

    def reject(self, project):
        project.status = PresentedService.STATUS[2]

    def end(self, project):
        project.status = PresentedService.STATUS[4]
