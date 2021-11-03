from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Shop, Product
from .serializers import ShopSerializer, ProductSerializer, ShopPreviewSerializer, ShopProductsPreviewSerializer

from scraping import scrape
from utils import utils


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

    def post(self, request, pk):
        response = {}
        request_data = request.data

        ser = self.serializer_class(data=request_data)
        if not ser.is_valid():
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        if ser.data.get('vendor') != pk:
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

    def get(self, request, pk):
        shops = self.query_set.filter(vendor_id=pk)
        ser = self.serializer_class(shops, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopProductsView(APIView):
    serializer_class = ProductSerializer

    def post(self, request, pk):    # pk is shop id
        """create all products with query_media json file"""
        response = {}

        shop = get_object_or_404(Shop, pk=pk)

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
        product_data = {}
        for post_data in media_query:
            product_data["shop"] = shop.pk
            product_data["shortcode"] = post_data['shortcode']
            product_data["display_image"] = f"media/shop/{instagram_username}/{post_data['id']}/display_image.jpg"
            product_data["title"] = f"آنلاین شاپ {instagram_username}، محصول {index}"
            product_data["description"] = post_data['edge_media_to_caption']['edges'][0]['node']['text']
            product_data["instagram_link"] = post_data['shortcode']

            serializer = self.serializer_class(data=product_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            index += 1

        return Response(status=status.HTTP_200_OK)


class ShopProductsPreviewView(APIView):
    serializer_class = ShopProductsPreviewSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects

    def get(self, request, *args, **kwargs):
        products_list = Product.objects.filter(shop__instagram_username=kwargs['ig_username'], price__isnull=False)
        ser = self.serializer_class(products_list, many=True)
        return Response(ser.data, status=status.HTTP_200_OK)


class ShopPreviewView(APIView):
    permission_classes = [AllowAny]
    query_set = Shop.objects.all()
    serializer_class = ShopPreviewSerializer

    def get(self, request, ig_username):
        try:
            shop = self.query_set.get(instagram_username=ig_username)
        except Shop.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ser = self.serializer_class(shop)
        return Response(ser.data, status=status.HTTP_200_OK)
