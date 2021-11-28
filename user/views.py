import random

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User, Otp
from .serializers import UserSerializer, CustomerSerializer, OtpSerializer, UserPhoneSerializer

from sms_service.sms_service import SMSService
from utils import utils


# Create your views here.
class UserView(APIView):
    permission_classes = [AllowAny]
    query_set = User.objects.all()

    def post(self, request):  # check user existence
        response = {}

        ser = UserPhoneSerializer(data=request.data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = ser.data.get('phone')

        try:
            self.query_set.get(phone=phone)
            response['user'] = 'found'
            return Response(response, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response['user'] = 'not found'
            return Response(response, status=status.HTTP_200_OK)

    def put(self, request):  # change user password
        response = {}

        try:
            phone = request.data['phone']
            password = request.data['password']
            user = self.query_set.get(phone=phone)
        except KeyError:
            response['error'] = ["شماره موبایل و رمز عبور الزامی است."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            response['error'] = ["کاربری با این شماره وجود ندارد."]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        user.set_password(raw_password=password)
        user.save()

        ser = UserSerializer(user)
        token_serializer = JSONWebTokenSerializer(data={"phone": user.phone, "password": password})
        token_serializer.is_valid(raise_exception=True)

        response.update(ser.data)
        response.update({"token": token_serializer.validated_data.get("token")})
        return Response(response, status=status.HTTP_200_OK)


class UserSignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    query_set = User.objects.all()

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


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    response = {}

    try:
        phone = request.data['phone']
    except KeyError:
        response["phone"] = ["This field is required."]
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    otp_code = random.randint(100000, 999999)

    try:
        SMSService().send_otp(phone=phone, otp=otp_code)
    except Exception as e:
        print(e)
        response['error'] = "problem in sending otp sms"
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    data = {
        "phone": phone,
        "otp_code": otp_code,
    }
    ser = OtpSerializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.save()
    response = ser.data
    response.pop("otp_code")
    return Response(response, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_otp_view(request):
    ser = OtpSerializer(data=request.data)
    if not ser.is_valid():
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    objects = Otp.objects.filter(phone=ser.data.get('phone'))
    response = {}

    if len(objects) == 0:
        response['error'] = ['شماره موبایل یافت نشد.']
        return Response(response, status=status.HTTP_404_NOT_FOUND)

    obj = objects.last()

    if obj.otp_code == request.data['otp_code']:
        valid_time = utils.is_expired_otp(obj.created_at)

        if not valid_time:
            response['otp_code'] = ['کد فعالسازی وارد شده منقضی شده است.']
            return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response(status=status.HTTP_200_OK)
    else:
        response['otp_code'] = ['کد فعالسازی وارد شده اشتباه است.']
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
