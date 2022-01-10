import json

from django.utils import timezone
from rest_framework.generics import get_object_or_404, ListCreateAPIView, DestroyAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAdminUser

from sms_service.sms_service import SMSService
from .models import Shop, Product, BankCredit, ProductAttribute, Post, Discount, TagLocation
from .serializers import ShopSerializer, ProductSerializer, ShopPublicSerializer, DiscountSerializer, \
    BankCreditSerializer, ProductAttributeSerializer, PostSerializer, \
    ProductImageSerializer, PostReadonlySerializer, TagLocationSerializer
from logger.serializers import IssueSerializer

from scraping.models import Scraper
from scraping.service import scrape
from utils import utils


class IsShopOwnerOrReadOnly(permissions.BasePermission):
    message = 'تغییر در فروشگاه مجاز نیست.'

    def has_object_permission(self, request, view, obj):
        print('in has_object_permission')
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


# Create your views here.
class ShopCreationRequestView(APIView):
    serializer_class = IssueSerializer

    def post(self, request):
        data = request.data
        data['user'] = request.user.pk
        data['phone'] = request.user.phone
        data = {
            'message': json.dumps(data),
            'location': 'SHOP CREATION REQUEST',
            'critical': False,
            'is_customer_project': False,
        }
        ser = self.serializer_class(data=data)
        ser.is_valid(raise_exception=True)
        ser.save()

        try:
            SMSService().send_otp(phone='09174347638', otp=0)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(status=status.HTTP_201_CREATED)


def get_free_scraper():
    scrapers = Scraper.objects.filter(is_working=False)
    count = 0
    scraper_index = 0

    if scrapers.count() == 0:
        raise Exception('All Scrapers Are Working')

    for i, scraper in enumerate(scrapers):
        if i == 0:
            count = scraper.scrape_count
            scraper_index = i
            continue
        if scraper.scrape_count < count:
            count = scraper.scrape_count
            scraper_index = i

    scraper = scrapers[scraper_index]
    scraper.is_working = True
    scraper.scrape_count += 1
    scraper.save()
    return scraper


class ShopMediaQueryView(APIView):
    instagram_username = ""
    extra_posts = []

    def __remove_extra_posts_dirs_and_images(self):
        """remove extra posts directory and images in media root for an instagram online shop"""

        removed_parents_id = []
        for extra_post in self.extra_posts[::-1]:  # reverse it because it's like stack, and want to pop
            if not extra_post.get('parent'):
                # it doesn't have parent so it is parent post
                pid = extra_post.get('id')
                self.__remove_extra_posts_dirs(pid)
                removed_parents_id.append(pid)
            else:
                # it's child post
                if extra_post.get('parent') not in removed_parents_id:
                    # its parent post was not removed
                    self.__remove_extra_posts_dirs(extra_post.get('parent'), extra_post.get('id'))

    def __remove_extra_posts_dirs(self, *dirs):
        """remove extra posts directory and directory contents in media root for an instagram online shop"""

        try:
            utils.remove_shop_media_directory(self.instagram_username, *dirs)
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}.")

    def __remove_extra_posts_media_query(self):
        """remove extra posts data from media query json file of an instagram page"""

        media_query_data = scrape.read_user_media_query_data(self.instagram_username)

        for extra_post in self.extra_posts[::-1]:
            """it should be reversed because extra_posts list is like stack,
            and it is possible to remove a parent before removing its child when it is reversed.
            So complexity will be reduced and function finished faster"""
            if not extra_post.get('parent'):
                # it was a parent post
                for mq in media_query_data:
                    if mq['id'] == extra_post['id']:
                        media_query_data.remove(mq)
                        break
            else:
                # it was a child post
                for parent in media_query_data:
                    if parent['id'] == extra_post['parent']:
                        for child in parent['children']:
                            if child['id'] == extra_post['id']:
                                parent['children'].remove(child)
                                break
                        break

        scrape.write_user_media_query_data(self.instagram_username, media_query_data)

    def post(self, request):
        """this method will scrape user instagram page, and get query_media data.
            next it will save the query media in a json file and return instagram profile info"""
        response = {}

        try:
            self.instagram_username = request.query_params['instagram_username']
        except KeyError:
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if Shop.objects.filter(instagram_username=self.instagram_username).exists():
            response["error"] = [f'مغازه {self.instagram_username} موجود است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            # data = scrape.scrape_instagram_media(scraper.username, scraper.password, self.instagram_username)
            # scrape.write_user_media_query_data(self.instagram_username, data)
            response = scrape.read_user_profile_info_data(self.instagram_username)
            # scraper.is_working = False
            # scraper.save()
            return Response(response, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            # scraper.is_working = False
            # scraper.save()
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            # scraper.is_working = False
            # scraper.save()
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

        page = request.query_params.get('page')
        if page is not None:
            page = int(page)

        try:
            # posts_preview_data = scrape.read_user_media_query_data(instagram_username)
            # scrape.save_preview_images(self.instagram_username, page)
            posts_preview_data = scrape.read_user_media_query_data(self.instagram_username)
            response_data = scrape.get_page_preview_data(self.instagram_username, page, posts_preview_data)
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
            Shop.objects.get(instagram_username=self.instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist:
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        self.__remove_extra_posts_dirs_and_images()
        self.__remove_extra_posts_media_query()

        return Response(status=status.HTTP_200_OK)


class ShopMediaQueryNewPostsView(APIView):
    instagram_username = ""
    extra_posts = []

    def __remove_extra_posts_dirs_and_images(self):
        """remove new extra posts directory and images in media root for an instagram online shop"""

        removed_parents_id = []
        for extra_post in self.extra_posts[::-1]:  # reverse it because it's like stack, and want to pop
            if not extra_post.get('parent'):
                # it doesn't have parent so it is parent post
                pid = extra_post.get('id')
                self.__remove_extra_posts_dirs(pid)
                removed_parents_id.append(pid)
            else:
                # it's child post
                if extra_post.get('parent') not in removed_parents_id:
                    # its parent post was not removed
                    self.__remove_extra_posts_dirs(extra_post.get('parent'), extra_post.get('id'))

    def __remove_extra_posts_dirs(self, *dirs):
        """remove extra posts directory and directory contents in media root for an instagram online shop"""

        try:
            utils.remove_shop_media_directory(self.instagram_username, *dirs)
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}.")

    def __remove_extra_posts_media_query(self):
        """remove extra posts data from media query json file of an instagram page"""

        media_query_data = scrape.read_user_new_media_query_data(self.instagram_username)

        for extra_post in self.extra_posts[::-1]:
            """it should be reversed because extra_posts list is like stack,
            and it is possible to remove a parent before removing its child when it is reversed.
            So complexity will be reduced and function finished faster"""
            if not extra_post.get('parent'):
                # it was a parent post
                for mq in media_query_data:
                    if mq['id'] == extra_post['id']:
                        media_query_data.remove(mq)
                        break
            else:
                # it was a child post
                for parent in media_query_data:
                    if parent['id'] == extra_post['parent']:
                        for child in parent['children']:
                            if child['id'] == extra_post['id']:
                                parent['children'].remove(child)
                                break
                        break

        scrape.write_user_new_media_query_data(self.instagram_username, media_query_data)

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
        except KeyError:
            response["error"] = ['آیدی پیج اینستاگرام الزامی است.']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # find scraper
        try:
            scraper = get_free_scraper()
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            data = scrape.scrape_new_instagram_media(scraper.username, scraper.password, shop.instagram_id,
                                                     last_post_shortcode)
            scrape.write_user_new_media_query_data(instagram_username, data)
            scraper.is_working = False
            scraper.save()
            return Response(data, status=status.HTTP_200_OK)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            scraper.is_working = False
            scraper.save()
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            scraper.is_working = False
            scraper.save()
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """this method will download new preview images of user instagram page
        from new media query json file. and save them in specific directory"""
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError:
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
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """this method will remove new extra post directories and new extra post data from json file"""
        response = {}

        try:
            self.instagram_username = request.query_params['instagram_username']
            self.extra_posts = request.data['extra_posts']
            user_pk = request.data['user_id']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            Shop.objects.get(instagram_username=self.instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist:
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        self.__remove_extra_posts_dirs_and_images()
        self.__remove_extra_posts_media_query()

        return Response(status=status.HTTP_200_OK)


class SaveMediaView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        response = {}

        try:
            instagram_username = request.query_params['instagram_username']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # find scraper
        try:
            scraper = get_free_scraper()
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            data = scrape.scrape_instagram_media(scraper.username, scraper.password, instagram_username)
            scrape.write_user_media_query_data(instagram_username, data)
            scraper.is_working = False
            scraper.save()
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            response["type"] = 'scraper error'
            scraper.is_working = False
            scraper.save()
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            response["type"] = 'system error'
            scraper.is_working = False
            scraper.save()
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
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(status=status.HTTP_201_CREATED)


class ShopView(APIView):
    serializer_class = ShopSerializer
    query_set = Shop.objects.all()

    def post(self, request, vendor_pk):
        response = {}
        request_data = request.data

        ser = self.serializer_class(data=request_data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        if ser.data.get('vendor') != vendor_pk:
            response["error"] = ['pk is not valid']
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        instagram_username = ser.data.get('instagram_username')

        # try:
        #     profile_pic_url = scrape.save_profile_image(instagram_username)
        # except scrape.CustomException as ex:
        #     response["error"] = [ex.message]
        #     return Response(response, status=ex.status)
        # except Exception as exc:
        #     response["error"] = [str(exc)]
        #     return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # request_data['profile_pic'] = profile_pic_url
        request_data['profile_pic'] = f"media/shop/{instagram_username}/profile_image.jpg"

        ser = self.serializer_class(data=request_data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def get(self, request, vendor_pk):
        shops = self.query_set.filter(vendor_id=vendor_pk)
        ser = self.serializer_class(shops, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


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
        except KeyError:
            response["error"] = ["آیدی فروشگاه ضروری است."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Shop.DoesNotExist:
            response["error"] = ["فروشگاه پیدا نشد."]
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            media_query = scrape.read_user_media_query_data(instagram_username)
        except Exception as exc:
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
            post_serializer.is_valid(raise_exception=True)
            post_serializer.save()

            product_image_data["post"] = post_serializer.data.get('id')
            product_image_data["display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/display_image.jpg"
            product_image_ser = self.product_image_serializer_class(data=product_image_data)
            product_image_ser.is_valid(raise_exception=True)
            product_image_ser.save()

            for index, child in enumerate(mq_item["children"]):
                if index == 0:
                    continue
                product_image_data["post"] = post_serializer.data.get('id')
                product_image_data[
                    "display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/{child['id']}/display_image.jpg "
                product_image_ser = self.product_image_serializer_class(data=product_image_data)
                product_image_ser.is_valid(raise_exception=True)
                product_image_ser.save()

        return Response(status=status.HTTP_200_OK)


class ShopProductView(CreateAPIView):
    serializer_class = ProductSerializer


class ShopBankCreditsView(ListCreateAPIView):
    serializer_class = BankCreditSerializer

    def get_queryset(self):
        return BankCredit.objects.filter(shop_id=self.kwargs['shop_pk'])


class ShopProductsPreviewView(APIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        posts_list = Post.objects.filter(shop__instagram_username=kwargs['ig_username']).order_by('id').reverse()
        posts_list = [p for p in posts_list if p.has_product]
        ser = self.serializer_class(posts_list, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


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


class PostEditView(UpdateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_url_kwarg = 'post_shortcode'
    lookup_field = 'shortcode'


class ProductDiscountView(APIView):
    serializer_class = DiscountSerializer
    query_set = Discount.objects.all()

    def post(self, request, product_pk):
        """ create a new discount for product"""
        product = get_object_or_404(Product, pk=product_pk)
        if request.data.get('product') != product.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        discount_ser = self.serializer_class(data=request.data)
        discount_ser.is_valid(raise_exception=True)
        discount_ser.save()

        product_ser = ProductSerializer(product)

        response = discount_ser.data
        response['product'] = product_ser.data

        return Response(response, status=status.HTTP_201_CREATED)

    def put(self, request, product_pk):
        """ this method will inactive the last discount of product """
        product = get_object_or_404(Product, pk=product_pk)
        if request.data.get('product') != product.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        discount = self.query_set.filter(product=product).last()
        if discount is None:
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
        ser.is_valid(raise_exception=True)
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
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)


class NewestProductsView(ListAPIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        posts = list(filter(lambda p: p.has_product, Post.objects.all()))
        return posts[:10]
