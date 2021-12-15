from rest_framework.generics import get_object_or_404, ListCreateAPIView, DestroyAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny

from .models import Shop, Product, BankCredit, ProductAttribute, Post, Discount
from .serializers import ShopSerializer, ProductSerializer, ShopPublicSerializer, DiscountSerializer, \
    BankCreditSerializer, ProductAttributeSerializer, PostSerializer, \
    ProductImageSerializer, PostReadonlySerializer, TagLocationSerializer

from scraping import scrape
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
class ShopMediaQueryView(APIView):
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

        media_query_data_copy = media_query_data.copy()
        for post_data in media_query_data_copy:
            if post_data['id'] in extra_posts_id_list:
                media_query_data.remove(post_data)

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
            data = scrape.scrape_instagram_media(self.instagram_username)
            scrape.write_user_media_query_data(self.instagram_username, data)
            response = scrape.read_user_profile_info_data(self.instagram_username)
            return Response(response, status=status.HTTP_200_OK)
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

        page = request.query_params.get('page')
        if page is not None:
            page = int(page)

        try:
            scrape.save_preview_images(self.instagram_username, page)
            response_data = scrape.get_page_preview_data(self.instagram_username, page)
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
            if request.user.pk != user_pk:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            Shop.objects.get(instagram_username=self.instagram_username, vendor_id=user_pk)
        except Shop.DoesNotExist:
            response["error"] = ["shop not found"]
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        self.__remove_extra_posts_dirs()
        self.__remove_extra_posts_media_query()

        return Response(status=status.HTTP_200_OK)


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

        try:
            profile_pic_url = scrape.save_profile_image(instagram_username)
        except scrape.CustomException as ex:
            response["error"] = [ex.message]
            return Response(response, status=ex.status)
        except Exception as exc:
            response["error"] = [str(exc)]
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        request_data['profile_pic'] = profile_pic_url

        ser = self.serializer_class(data=request_data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def get(self, request, vendor_pk):
        shops = self.query_set.filter(vendor_id=vendor_pk)
        ser = self.serializer_class(shops, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopPostView(APIView):
    post_serializer_class = PostSerializer
    product_image_serializer_class = ProductImageSerializer

    def post(self, request, shop_pk):  # pk is shop id
        """create all posts and products with query_media json file"""
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

        index = 1
        post_data = {}
        product_image_data = {}

        for mq_item in media_query:
            if len(mq_item['edge_media_to_caption']['edges']) > 0:
                post_caption = mq_item['edge_media_to_caption']['edges'][0]['node']['text']
            else:
                post_caption = ''

            post_data["shop"] = shop.pk
            post_data["shortcode"] = mq_item['shortcode']
            post_data["description"] = post_caption
            post_data["instagram_link"] = mq_item['shortcode']

            post_serializer = self.post_serializer_class(data=post_data)
            post_serializer.is_valid(raise_exception=True)
            post_serializer.save()

            # TODO create more product images
            product_image_data["post"] = post_serializer.data.get('id')
            product_image_data["display_image"] = f"media/shop/{instagram_username}/{mq_item['id']}/display_image.jpg"

            product_image_ser = self.product_image_serializer_class(data=product_image_data)
            product_image_ser.is_valid(raise_exception=True)
            product_image_ser.save()

            # TODO create product if it is necessary

            index += 1

        return Response(status=status.HTTP_200_OK)

    def get(self, request, shop_pk):
        shop = get_object_or_404(Shop, pk=shop_pk)
        posts = Post.objects.filter(shop_id=shop.id)
        ser = self.post_serializer_class(posts, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopProductView(CreateAPIView):
    serializer_class = ProductSerializer


class ShopBankCreditsView(ListCreateAPIView):
    serializer_class = BankCreditSerializer
    queryset = BankCredit.objects.all()

    def get_queryset(self):
        shop_pk = self.kwargs.get('shop_pk')
        return self.queryset.filter(shop_id=shop_pk)


class ShopProductsPreviewView(APIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        posts_list = Post.objects.filter(shop__instagram_username=kwargs['ig_username'],
                                         productimage__product__original_price__isnull=False)
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


class PostPublicView(RetrieveAPIView):
    serializer_class = PostReadonlySerializer
    permission_classes = [AllowAny]
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


class ProductTagCreateView(CreateAPIView):
    serializer_class = TagLocationSerializer
