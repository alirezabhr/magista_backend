from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import IssueSerializer


# Create your views here.
class IssueView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        for item in data:
            item['user'] = request.user.pk

        ser = self.serializer_class(data=data, many=True)
        ser.is_valid(raise_exception=True)
        ser.save()

        for s in ser.data:
            if s['critical']:
                pass    # TODO send email

        return Response(ser.data, status=status.HTTP_201_CREATED)
