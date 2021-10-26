import random

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import JSONWebTokenSerializer

from .models import User, Otp, Shop
from .serializers import UserSerializer, ShopSerializer, CustomerSerializer, OtpSerializer, UserPhoneSerializer

from scraping import scrape
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


class ShopView(APIView):
    serializer_class = ShopSerializer
    query_set = Shop.objects.all()

    def post(self, request, pk):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        shops = self.query_set.filter(vendor_id=pk)
        ser = self.serializer_class(shops, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class UserMediaView(APIView):
    instagram_username = ""
    extra_posts = []

    def __remove_extra_posts_dirs(self):
        """remove extra posts directory and directory contents in media root for an instagram online shop"""

        for extra_post in self.extra_posts:
            try:
                utils.remove_shop_media_directory(self.instagram_username, extra_post.get('id'))
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")

    def __remove_extra_posts_media_query(self):
        """remove extra posts data from media query json file of an instagram page"""

        extra_posts_id_list = [post['id'] for post in self.extra_posts]
        media_query_data = scrape.read_user_media_query_data(self.instagram_username)

        index = 0
        for post_data in media_query_data:
            if post_data['id'] in extra_posts_id_list:
                media_query_data.pop(index)
            index += 1

        scrape.write_user_media_query_data(self.instagram_username, media_query_data)

    def post(self, request):
        """this method will scrape user instagram page, and get query_media data.
            next it will save the query media in a json file and return status"""

        response = {}

        try:
            self.instagram_username = request.query_params['instagram_username']
        except KeyError:
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = scrape.scrape_instagram_media(self.instagram_username)
            scrape.write_user_media_query_data(self.instagram_username, data)
            return Response(status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """this method will download all preview images of user instagram page,
            from media query json file. and save them in specific directory"""

        response = {}

        try:
            self.instagram_username = request.query_params['instagram_username']
        except KeyError:
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            scrape.save_preview_images(self.instagram_username)
            response_data = scrape.get_page_preview_data(self.instagram_username)
            return Response(response_data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """this method will remove extra post directories and extra post data from json file"""
        response = {}

        try:
            self.instagram_username = request.query_params['instagram_username']
            self.extra_posts = request.data['extra_posts']
            user_pk = request.data['user_id']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = Shop.objects.get(instagram_username=self.instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist:
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        self.__remove_extra_posts_dirs()
        self.__remove_extra_posts_media_query()

        # TODO create all products of this user with the rest of the posts

        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    response = {}

    try:
        phone = request.data['phone']
    except KeyError:
        response["phone"] = ["This field is required."]
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    otp_code = random.randint(10000, 99999)

    # try:
    #     SMSService().send_otp(phone=phone, otp=otp_code)
    # except Exception as e:
    #     print(e)
    #     response['error'] = "problem in sending otp sms"
    #     return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
