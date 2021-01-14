from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BarberS.utils import get_error_obj
from barber.serializers import ProjectSerializer, ServiceSchemaSerializer
from client.models import PresentedService, Service, Barber, ServiceSchema


class ServiceHandler(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()

    def create_or_update(self, request, service_id, barber):
        try:
            cost = request.data['cost']
        except:
            return Response(get_error_obj('wrong_parameters', 'no parameter cost sent'),
                            status=status.HTTP_400_BAD_REQUEST)
        schema = ServiceSchema.objects.filter(service_schema_id=service_id).first()
        if not schema:
            return Response(get_error_obj('no_data_found', 'service schema was not found'),
                            status=status.HTTP_404_NOT_FOUND)
        if schema.lower_limit != 0 and schema.lower_limit > cost:
            return Response(get_error_obj('wrong_parameters', 'cost is out of range'), status=status.HTTP_409_CONFLICT)
        if schema.upper_limit != -1 and schema.upper_limit < cost:
            return Response(get_error_obj('wrong_parameters', 'cost is out of range'), status=status.HTTP_409_CONFLICT)
        service = Service.objects.filter(schema__service_schema_id=service_id, barber=barber).first()
        if not service:
            try:
                service = Service(service_id="service_{}".format(Service.objects.count() + 1))
            except:
                service = Service(service_id="service_{}".format(Service.objects.all().last().pk + 1))
            service.barber = barber
            service.schema = schema
        service.cost = cost
        service.save()
        return Response({"status": 200})

    def delete(self, service_id, barber):
        service = Service.objects.filter(schema__service_schema_id=service_id, barber=barber).first()
        if not service:
            return Response(get_error_obj('no_data_found'), status=status.HTTP_400_BAD_REQUEST)
        service.delete()
        return Response({"status": 200})

    def get(self, request):
        try:
            schemas = ServiceSchema.objects.all()
            schemas = ServiceSchemaSerializer(schemas, many=True)
            return Response(schemas.data)
        except Exception as e:
            return Response(get_error_obj('server_error', str(e)),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # general problem

    def post(self, request):
        user = request.user
        try:
            barber = Barber.objects.filter(user=user).first()
        except:
            return Response(get_error_obj('access_denied'), status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response(get_error_obj('access_denied'), status=status.HTTP_401_UNAUTHORIZED)
        action = 1
        if 'action' in request.data:
            action = request.data['action']
        try:
            service_id = request.data['service_id']
        except:
            return Response(get_error_obj('wrong_parameters', 'no service id was sent'),
                            status=status.HTTP_400_BAD_REQUEST)
        if action == 1:
            return self.create_or_update(request, service_id, barber)
        elif action == 2:
            return self.delete(service_id, barber)
        else:
            return Response(get_error_obj('wrong_parameters', 'this action is not in action list'),
                            status=status.HTTP_400_BAD_REQUEST)


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
            return Response(get_error_obj('access_denied'), status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response(get_error_obj('access_denied'), status=status.HTTP_401_UNAUTHORIZED)
        project_status = request.GET.get('status')
        offset = int(request.GET.get('offset'))
        if not offset:
            offset = 0
        if not project_status:
            # return Response(get_error_obj('wrong_parameters', 'no project status declared'),
            #                 status=status.HTTP_400_BAD_REQUEST)
            queryset = self.queryset
        elif project_status == 'unverified':
            queryset = self.queryset.filter(status=PresentedService.STATUS[0][0])
        elif project_status == 'in_progress':
            queryset = self.queryset.filter(status=PresentedService.STATUS[2][0])
        else:
            queryset = self.queryset.filter(status=PresentedService.STATUS[3][0])
        size = queryset.count()
        if offset > size:
            return Response(get_error_obj('wrong_parameters'), status=status.HTTP_400_BAD_REQUEST)
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
            return Response(get_error_obj('access_denied'), status=status.HTTP_404_NOT_FOUND)
        if not barber.is_verified:
            return Response(get_error_obj('access_denied'), status=status.HTTP_401_UNAUTHORIZED)
        try:
            date = request.data['date']
            year, month, day = date.split('-')
            projects = self.queryset.filter(reserveTime__year=year, reserveTime__month=month, reserveTime__day=day)
            projects = ProjectSerializer(projects, many=True)
            return Response(projects.data)
        except:
            return Response(get_error_obj('server_error'), status=status.HTTP_400_BAD_REQUEST)


class ProjectHandler(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PresentedService.objects.all()
    ACTIONS = ['verify', 'reject', 'end']

    def post(self, request, action):
        if action not in self.ACTIONS:
            return Response(get_error_obj('wrong_parameters', 'this action is not in action list'),
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            project_id = request.data['reserved_service_id']
        except:
            return Response(get_error_obj('wrong_parameters', 'no reserved service id sent'),
                            status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        i_barber = Barber.objects.filter(user=user).first()
        project = self.queryset.filter(project_id=project_id).first()
        if not project:
            return Response(get_error_obj('no_data_found', 'no reserved service found for this id'),
                            status=status.HTTP_400_BAD_REQUEST)
        if project.barber.barber_id != i_barber.barber_id:
            return Response(get_error_obj('access_denied', 'you are not the owner of this reserved service'),
                            status=status.HTTP_401_UNAUTHORIZED)
        res = 0
        if action == self.ACTIONS[0]:
            res = self.verify(project)
        elif action == self.ACTIONS[1]:
            res = self.reject(project)
        else:
            res = self.end(project)
        project.save()
        if res != 0:
            return Response(get_error_obj('not_allowed_action'), status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": 200})

    def verify(self, project):
        if project.status == PresentedService.STATUS[0][0]:
            project.status = PresentedService.STATUS[2][0]
            return 0
        return 1

    def reject(self, project):
        if project.status == PresentedService.STATUS[0][0]:
            project.status = PresentedService.STATUS[1][0]
            return 0
        return 1

    def end(self, project):
        if project.status == PresentedService.STATUS[2][0]:
            project.status = PresentedService.STATUS[3][0]
            return 0
        return 1
