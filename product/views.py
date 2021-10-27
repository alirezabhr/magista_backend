from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from user.models import Shop
from .models import Product
from .serializers import ProductSerializer

from scraping import scrape


# Create your views here.
class ShopProductsView(APIView):
    serializer_class = ProductSerializer

    def post(self, request):
        """create all products with query_media json file"""
        response = {}

        try:
            shop_id = request.data['shop']
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
            product_data["short_code"] = post_data['shortcode']
            product_data["display_image"] = f"media/shop/{instagram_username}/{post_data['id']}/display_image.jpg"
            product_data["title"] = f"آنلاین شاپ {instagram_username}، محصول {index}"
            product_data["description"] = post_data['edge_media_to_caption']['edges'][0]['node']['text']
            product_data["instagram_link"] = post_data['shortcode']

            serializer = self.serializer_class(data=product_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            index += 1

        return Response(status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    serializer_class = ProductSerializer

    def get(self, request, shortcode):
        product = get_object_or_404(Product, shortcode=shortcode)
        ser = self.serializer_class(product)
        return Response(ser.data, status=status.HTTP_200_OK)
