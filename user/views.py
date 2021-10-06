from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User
from .serializers import UserSerializer, ShopSerializer, CustomerSerializer


# Create your views here.
class UserSignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserSerializer
    query_set = User.objects.all()
    permission_classes = [AllowAny]

    def post(self, request):
        token_serializer = JSONWebTokenSerializer(data=request.data)

        if token_serializer.is_valid():
            user = self.query_set.get(phone=request.data.get("phone"))
            ser = self.serializer_class(user)

            result = {
                "token": token_serializer.validated_data.get("token"),
                "user": ser.data,
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerView(APIView):
    serializer_class = CustomerSerializer

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class ShopView(APIView):
    serializer_class = ShopSerializer

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
