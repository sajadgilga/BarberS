from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from client.models import Barber


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def best_barbers(request):
    LIMIT = 10
    offset = int(request.GET.get('offset'))
    if not offset:
        offset = 0
    offset = LIMIT * offset
    size = len(Barber.objects.all())
    if offset > size:
        return Response({"status": 301}, status=status.HTTP_400_BAD_REQUEST)
    elif offset + LIMIT < size:
        barbers = Barber.objects.all().order_by('point')[offset: offset + LIMIT]
    else:
        barbers = Barber.objects.all().order_by('point')[offset:]
