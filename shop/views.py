import random

from django.utils import timezone
from rest_framework.generics import get_object_or_404, ListCreateAPIView, DestroyAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.pagination import PageNumberPagination

from logger.log_sentry import log_message_sentry
from sms_service.sms_service import SMSService
from .models import Shop, Product, BankCredit, ProductAttribute, Post, ProductDiscount, TagLocation, ProductImage, \
    ShopDiscount, Shipment, DeliveryPrice, ShopCreationStep, Category
from .serializers import ShopSerializer, ProductSerializer, ShopPublicSerializer, ProductDiscountSerializer, \
    BankCreditSerializer, ProductAttributeSerializer, PostSerializer, \
    ProductImageSerializer, PostReadonlySerializer, TagLocationSerializer, ProductImageReadonlySerializer, \
    ShopDiscountSerializer, ShipmentSerializer, ShopCreationStepSerializer, CategorySerializer

from scraping.service import scrape
from utils import utils

from sentry_sdk import capture_exception


class IsShopOwnerOrReadOnly(permissions.BasePermission):
    message = 'تغییر در فروشگاه مجاز نیست.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        print(request.user)
        print(obj)
        return obj.vendor == request.user

    # def has_permission(self, request, view):
    #     print('in has_permission')
    #     print(request.user)
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     return False


class PostsListPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'


# Create your views here.
class CategoryView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer


class ShopCreationView(APIView):
    serializer_class = ShopCreationStepSerializer

    @classmethod
    def change_shop_creation_step(cls, instagram_username: str, step: str):
        try:
            obj = ShopCreationStep.objects.get(instagram_username=instagram_username)
        except ShopCreationStep.DoesNotExist:
            return
        obj.step = step
        obj.save()

    def get(self, request, ig_username):
        creation_step_obj = get_object_or_404(ShopCreationStep, instagram_username=ig_username)
        ser = self.serializer_class(creation_step_obj)
        return Response(ser.data)

    def post(self, request, ig_username):
        data = {
            'vendor': request.data.get('vendor'),
            'instagram_username': ig_username,
            'email': '' if request.data.get('email') is None else request.data.get('email')
        }
        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()

        try:
            SMSService().shop_request_sms()
        except Exception as e:
            capture_exception(error=e)

        return Response(ser.data, status=status.HTTP_201_CREATED)


class ShopMediaQueryView(APIView):
    def post(self, request):
        """this method will scrape user instagram page, and get query_media data.
            next it will save the query media in a json file and return instagram profile info"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            shop_creation_step_obj = ShopCreationStep.objects.get(instagram_username=instagram_username)
            if shop_creation_step_obj.step == ShopCreationStep.CREATED:
                response["error"] = [f'فروشگاه {instagram_username} موجود است.']
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except ShopCreationStep.DoesNotExist:   # shop didn't request ever
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # if Shop.objects.filter(instagram_username=instagram_username).exists():
        #     response["error"] = [f'فروشگاه {instagram_username} موجود است.']
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            # data = scrape.scrape_instagram_media(scraper.username, scraper.password, instagram_username)
            # scrape.write_user_media_query_data(instagram_username, data)
            response = scrape.read_user_profile_info_data(instagram_username)
            return Response(response, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """this method will download all preview images of user instagram page,
            from media query json file. and save them in specific directory"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        page = request.query_params.get('page')
        if page is not None:
            page = int(page)

        try:
            # posts_preview_data = scrape.read_user_media_query_data(instagram_username)
            # scrape.save_preview_images(instagram_username, page)
            posts_preview_data = scrape.read_user_media_query_data(instagram_username)
            response_data = scrape.get_page_preview_data(instagram_username, page, posts_preview_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """this method will remove extra post directories and extra post data from json file"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
            extra_posts = request.data['extra_posts']
            user_pk = request.data['user_id']
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = [str(e)]
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            Shop.objects.get(instagram_username=instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist as e:
            capture_exception(error=e)
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        try:
            media_query_data = scrape.read_user_media_query_data(instagram_username)
            utils.remove_extra_posts_dirs_and_images(extra_posts)
            new_media_query_data = utils.remove_extra_posts_media_query(media_query_data, extra_posts)
            scrape.write_user_media_query_data(instagram_username, new_media_query_data)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class ShopMediaQueryNewPostsView(APIView):

    def post(self, request):
        """this method will scrape user instagram page, and get new posts query_media data.
            next it will add them in the query media json file"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
            shop = get_object_or_404(Shop, instagram_username=instagram_username)
            last_post = Post.objects.filter(shop_id=shop.id).last()
            if last_post is None:  # shop does not exists or doesn't have any posts
                return Response(status=status.HTTP_400_BAD_REQUEST)
            last_post_shortcode = last_post.shortcode
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        shop.last_scrape = timezone.now()
        shop.save()

        try:
            data = scrape.scrape_new_instagram_media(shop.instagram_id, last_post_shortcode)
            scrape.write_user_new_media_query_data(instagram_username, data)
            return Response(data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """this method will download new preview images of user instagram page
        from new media query json file. and save them in specific directory"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        page = request.query_params.get('page')
        if page is not None:
            page = int(page)

        try:
            posts_preview_data = scrape.read_user_new_media_query_data(instagram_username)
            scrape.save_preview_images(instagram_username, page, posts_preview_data)
            response_data = scrape.get_page_preview_data(instagram_username, page, posts_preview_data)
            return Response(response_data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """this method will remove new extra post directories and new extra post data from json file"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
            extra_posts = request.data['extra_posts']
            user_pk = request.data['user_id']
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            Shop.objects.get(instagram_username=instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist as e:
            capture_exception(error=e)
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        try:
            media_query_data = scrape.read_user_new_media_query_data(instagram_username)
            utils.remove_extra_posts_dirs_and_images(extra_posts)
            new_media_query_data = utils.remove_extra_posts_media_query(media_query_data, extra_posts)
            scrape.write_user_new_media_query_data(instagram_username, new_media_query_data)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)


class SaveMediaView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            data = scrape.scrape_instagram_media(instagram_username)
            scrape.write_user_media_query_data(instagram_username, data)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        has_next = True
        page = 1
        posts_preview_data = scrape.read_user_media_query_data(instagram_username)
        while has_next:
            scrape.save_preview_images(instagram_username, page, posts_preview_data)
            response_data = scrape.get_page_preview_data(instagram_username, page, posts_preview_data)
            has_next = response_data['has_next']
            page += 1

        try:
            scrape.save_profile_image(instagram_username)
        except scrape.CustomException as ex:
            capture_exception(error=ex)
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(status=status.HTTP_201_CREATED)


class ShopVendorView(APIView):
    serializer_class = ShopSerializer

    def create_default_shipment(self, shop_id):
        data = {
            "shop": shop_id,
            "send_everywhere": True,
            "has_national_post": True,
            "has_online_delivery": False,
            "national_post": {
                "type": DeliveryPrice.DeliveryType.NATIONAL_POST,
                "base": 13000,
                "per_kilo": 2700
            },
            "online_delivery": None,
            "city_cost": Shipment.FreeDelivery.NOT_FREE,
            "country_cost": Shipment.FreeDelivery.NOT_FREE,
            "city_free_cost_from": None,
            "country_free_cost_from": None
        }
        ser = ShipmentSerializer(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return ser.data

    def post(self, request, vendor_pk):
        response = {}
        data = request.data

        try:
            vendor_id = data['vendor']
            instagram_username = data['instagram_username']
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if vendor_id != vendor_pk:
            response["error"] = ['pk is not valid']
            log_message_sentry('ShopView post', response, request.data)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        data['last_scrape'] = timezone.now().__str__()
        data['profile_pic'] = f"media/shop/{instagram_username}/profile_image.jpg"

        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            log_message_sentry('ShopView post', ser.errors, request.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()

        shipment_data = self.create_default_shipment(ser.data.get('id'))
        response = ser.data
        response['delivery'] = shipment_data

        ShopCreationView.change_shop_creation_step(instagram_username, ShopCreationStep.FORM_SUBMITTED)

        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, vendor_pk):
        created_shops = ShopCreationStep.objects.filter(vendor_id=vendor_pk, step__exact=ShopCreationStep.CREATED)
        shops = []
        for created_shop in created_shops:
            shops.append(Shop.objects.get(instagram_username=created_shop.instagram_username))
        ser = self.serializer_class(shops, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopView(RetrieveAPIView):
    # permission_classes = [IsShopOwner, IsAdminUser]   # TODO change the permission
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    lookup_field = 'instagram_username'
    lookup_url_kwarg = 'ig_username'


class ShopShipmentView(CreateAPIView):
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()

    def put(self, request, shop_pk):
        shipment = get_object_or_404(Shipment, shop=shop_pk)
        ser = self.serializer_class(shipment, data=request.data)
        if not ser.is_valid():
            log_message_sentry('ShopShipmentView put', ser.errors, request.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopBioView(APIView):
    serializer_class = ShopSerializer

    def put(self, request, shop_pk):
        try:
            bio = request.data['bio']
        except KeyError as e:
            capture_exception(error=e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        shop = get_object_or_404(Shop, id=shop_pk)
        ser = self.serializer_class(shop)
        data = ser.data
        data['bio'] = bio
        ser = self.serializer_class(shop, data=data)
        if not ser.is_valid():
            log_message_sentry('ShopBioView put', ser.errors, request.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopInflationView(APIView):

    def increase_price(self, price, percent):
        price = (price * (100 + percent)) // 100
        price = (price // 100) * 100  # 12387 -> 12300
        return price

    def post(self, request, shop_pk):
        percent = request.data.get('percent')
        if percent is None:
            log_message_sentry('ShopInflationView post', {'error': 'percent is invalid'}, request.data, level='error')
            return Response(status=status.HTTP_400_BAD_REQUEST)

        shop = get_object_or_404(Shop, id=shop_pk)
        products = Product.objects.filter(image__post__shop=shop)
        for product in products:
            product.original_price = self.increase_price(product.original_price, percent)
            product.save()

        return Response(status=status.HTTP_200_OK)


class ShopDiscountView(ListAPIView):
    serializer_class = ShopDiscountSerializer

    def get_queryset(self):
        return ShopDiscount.objects.filter(shop_id=self.kwargs['shop_pk']).order_by('id').reverse()

    def generate_discount_code(self):
        # generate a random discount code with a length of 4 starts with
        return ''.join(random.choice('123456789') for _ in range(4))

    def generate_unique_code(self, shop_pk):
        qs = ShopDiscount.objects.filter(shop_id=shop_pk)
        shop_discount_code_list = [sd.code for sd in qs]
        code = self.generate_discount_code()
        while code in shop_discount_code_list:
            code = self.generate_discount_code()
        return code

    def post(self, request, shop_pk):
        get_object_or_404(Shop, id=shop_pk)
        code = self.generate_unique_code(shop_pk)
        data = request.data
        data['code'] = code

        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            log_message_sentry('ShopDiscountView post', ser.errors, request.data, level='error')
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()

        return Response(ser.data, status=status.HTTP_201_CREATED)


class ShopPostView(ListAPIView):
    # GET Method
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(shop_id=self.kwargs['shop_pk']).order_by('id').reverse()

    # POST Method
    product_image_serializer_class = ProductImageSerializer

    def post(self, request, shop_pk):  # pk is shop id
        """create all posts and product images with query_media json file"""
        response = {}

        shop = get_object_or_404(Shop, pk=shop_pk)

        try:
            shop_id = shop.pk
            instagram_username = request.data['instagram_username']
            shop = Shop.objects.get(pk=shop_id, instagram_username=instagram_username)
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ["آیدی فروشگاه ضروری است."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Shop.DoesNotExist as e:
            capture_exception(error=e)
            response["error"] = ["فروشگاه پیدا نشد."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            media_query = scrape.read_user_media_query_data(instagram_username)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        post_data = {}
        product_image_data = {}

        for mq_item in media_query[::-1]:  # it should be reversed to create older instagram posts first
            if 'edge_media_to_caption' in mq_item and 'edges' in mq_item['edge_media_to_caption'] and len(
                    mq_item['edge_media_to_caption']['edges']) > 0:
                post_caption = mq_item['edge_media_to_caption']['edges'][0]['node']['text']
            else:
                post_caption = ''

            post_data["shop"] = shop.pk
            post_data["shortcode"] = mq_item['shortcode']
            post_data["description"] = post_caption
            post_data["instagram_link"] = mq_item['shortcode']

            post_serializer = self.serializer_class(data=post_data)
            if not post_serializer.is_valid():
                log_message_sentry('ShopPostView post post_serializer error', post_serializer.errors, request.data,
                                   level='error')
                return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            post_serializer.save()

            product_image_data["post"] = post_serializer.data.get('id')
            product_image_data["display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/display_image.jpg"
            product_image_ser = self.product_image_serializer_class(data=product_image_data)
            if not product_image_ser.is_valid():
                log_message_sentry('ShopPostView post product_image_ser error', product_image_ser.errors, request.data,
                                   level='error')
                return Response(product_image_ser.errors, status=status.HTTP_400_BAD_REQUEST)
            product_image_ser.save()

            for index, child in enumerate(mq_item["children"]):
                if index == 0:
                    continue
                product_image_data["post"] = post_serializer.data.get('id')
                product_image_data[
                    "display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/{child['id']}/display_image.jpg "
                product_image_ser = self.product_image_serializer_class(data=product_image_data)
                if not product_image_ser.is_valid():
                    log_message_sentry('ShopPostView post product_image_ser error in for loop',
                                       product_image_ser.errors, request.data, level='error')
                    return Response(product_image_ser.errors, status=status.HTTP_400_BAD_REQUEST)
                product_image_ser.save()

        ShopCreationView.change_shop_creation_step(instagram_username, ShopCreationStep.CREATED)

        return Response(status=status.HTTP_200_OK)


class ShopNewPostView(APIView):
    serializer_class = PostSerializer
    product_image_serializer_class = ProductImageSerializer

    def post(self, request, shop_pk):  # pk is shop id
        """create new posts and product images with new_media_query json file"""
        response = {}

        shop = get_object_or_404(Shop, pk=shop_pk)

        try:
            shop_id = shop.pk
            instagram_username = request.data['instagram_username']
            shop = Shop.objects.get(pk=shop_id, instagram_username=instagram_username)
        except KeyError as e:
            capture_exception(error=e)
            response["error"] = ["آیدی فروشگاه ضروری است."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Shop.DoesNotExist as e:
            capture_exception(error=e)
            response["error"] = ["فروشگاه پیدا نشد."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            media_query = scrape.read_user_new_media_query_data(instagram_username)
        except Exception as exc:
            capture_exception(error=exc)
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        post_data = {}
        product_image_data = {}

        for mq_item in media_query[::-1]:  # it should be reversed to create older instagram posts first
            if 'edge_media_to_caption' in mq_item and 'edges' in mq_item['edge_media_to_caption'] and len(
                    mq_item['edge_media_to_caption']['edges']) > 0:
                post_caption = mq_item['edge_media_to_caption']['edges'][0]['node']['text']
            else:
                post_caption = ''

            post_data["shop"] = shop.pk
            post_data["shortcode"] = mq_item['shortcode']
            post_data["description"] = post_caption
            post_data["instagram_link"] = mq_item['shortcode']

            post_serializer = self.serializer_class(data=post_data)
            if not post_serializer.is_valid():
                log_message_sentry('ShopNewPostView post post_serializer', post_serializer.errors,
                                   request.data, level='error')
                return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            post_serializer.save()

            product_image_data["post"] = post_serializer.data.get('id')
            product_image_data["display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/display_image.jpg"
            product_image_ser = self.product_image_serializer_class(data=product_image_data)
            if not product_image_ser.is_valid():
                log_message_sentry('ShopNewPostView post product_image_ser', product_image_ser.errors,
                                   request.data, level='error')
                return Response(product_image_ser.errors, status=status.HTTP_400_BAD_REQUEST)
            product_image_ser.save()

            for index, child in enumerate(mq_item["children"]):
                if index == 0:
                    continue
                product_image_data["post"] = post_serializer.data.get('id')
                product_image_data[
                    "display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/{child['id']}/display_image.jpg "
                product_image_ser = self.product_image_serializer_class(data=product_image_data)
                if not product_image_ser.is_valid():
                    log_message_sentry('ShopNewPostView post product_image_ser in for loop', product_image_ser.errors,
                                       request.data, level='error')
                    return Response(product_image_ser.errors, status=status.HTTP_400_BAD_REQUEST)
                product_image_ser.save()

        return Response(status=status.HTTP_200_OK)


class ShopProductView(CreateAPIView):
    serializer_class = ProductSerializer


class ShopBankCreditsView(ListCreateAPIView):
    serializer_class = BankCreditSerializer

    def get_queryset(self):
        return BankCredit.objects.filter(shop_id=self.kwargs['shop_pk'])


class ShopProductsPreviewView(ListAPIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]

    # pagination_class = PostsListPagination

    def get_queryset(self):
        qs = Post.objects.filter(shop__instagram_username=self.kwargs['ig_username']).order_by('id').reverse()
        return [p for p in qs if p.has_product]


class ShopPublicView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Shop.objects.all()
    serializer_class = ShopPublicSerializer
    lookup_field = 'instagram_username'
    lookup_url_kwarg = 'ig_username'


class ProductView(RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'product_pk'
    lookup_field = 'pk'

    def delete(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        product.is_deleted = True
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostPublicView(RetrieveAPIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]
    queryset = Post.objects.all()
    lookup_url_kwarg = 'post_shortcode'
    lookup_field = 'shortcode'


class PostProductImagesPublicView(ListAPIView):
    serializer_class = ProductImageReadonlySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ProductImage.objects.filter(post__shortcode=self.kwargs['post_shortcode']).order_by('id')


class PostEditView(UpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_url_kwarg = 'post_shortcode'
    lookup_field = 'shortcode'


class ProductDiscountView(APIView):
    serializer_class = ProductDiscountSerializer
    query_set = ProductDiscount.objects.all()

    def post(self, request, product_pk):
        """ create a new discount for product"""
        product = get_object_or_404(Product, pk=product_pk)
        if request.data.get('product') != product.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        discount_ser = self.serializer_class(data=request.data)
        if not discount_ser.is_valid():
            log_message_sentry('ProductDiscountView post', discount_ser.errors, request.data)
            return Response(discount_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        discount_ser.save()

        product_ser = ProductSerializer(product)

        response = discount_ser.data
        response['product'] = product_ser.data

        return Response(response, status=status.HTTP_201_CREATED)

    def put(self, request, product_pk):
        """ this method will inactive the last discount of product """
        product = get_object_or_404(Product, pk=product_pk)
        if request.data.get('product') != product.id:
            log_message_sentry('ProductDiscountView put',
                               {'error': 'product id in query is not equal to product in request data'}, request.data)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        discount = self.query_set.filter(product=product).last()
        if discount is None:
            log_message_sentry('ProductDiscountView put',
                               {'error': 'discount is None'}, request.data)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        discount.is_active = False
        discount.save()
        return Response(status=status.HTTP_200_OK)


class ProductAttributeCreateView(APIView):
    serializer_class = ProductAttributeSerializer

    def post(self, request, *args, **kwargs):
        product_pk = kwargs.get('product_pk')
        data = request.data
        data['product'] = product_pk
        ser = self.serializer_class(data=data)
        if not ser.is_valid():
            log_message_sentry('ProductAttributeCreateView post', ser.errors, request.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class ProductAttributeDeleteView(DestroyAPIView):
    serializer_class = ProductAttributeSerializer

    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk')
        attribute_id = self.kwargs.get('pk')
        return ProductAttribute.objects.filter(product_id=product_pk, pk=attribute_id)


class ProductTagView(CreateAPIView):
    serializer_class = TagLocationSerializer

    def put(self, request):
        product = get_object_or_404(Product, pk=request.data.get('product'))
        try:
            tag = product.tag
        except TagLocation.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ser = self.serializer_class(tag, data=request.data)
        if not ser.is_valid():
            log_message_sentry('ProductTagView put', ser.errors, request.data)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)
