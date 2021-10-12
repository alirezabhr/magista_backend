from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User
from .serializers import UserSerializer, ShopSerializer, CustomerSerializer

from scraping import scrape


# Create your views here.
class UserSignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            user = ser.save()
            password = self.request.data.get("password")
            token_serializer = JSONWebTokenSerializer(data={"phone": user.phone, "password": password})
            token_serializer.is_valid(raise_exception=True)
            response_data = ser.data
            response_data.update({"token": token_serializer.validated_data.get("token")})
            return Response(response_data, status=status.HTTP_201_CREATED)
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
            response_data = ser.data
            response_data.update({"token": token_serializer.validated_data.get("token")})
            return Response(response_data, status=status.HTTP_200_OK)
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


class UserMediaView(APIView):
    def get(self, request):
        try:
            instagram_username = request.data['instagram_username']
        except KeyError:
            response = {
                'error': 'instagram username is required'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            response_data = scrape.scrape_instagram_media(instagram_username)
            return Response(response_data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response = {"error": ex.message}
            return Response(response, status=ex.status)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
