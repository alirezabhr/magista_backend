from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Product
from shop.serializers import ProductReadonlySerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def homepage_images_url(request):
    rsp = ['media/source/sale1.png', 'media/source/autumn_sale.png']
    return Response(rsp, status=status.HTTP_200_OK)


class NewestProductsView(ListAPIView):
    serializer_class = ProductReadonlySerializer
    permission_classes = [AllowAny]

    MAXIMUM_PRODUCTS_FROM_ONE_SHOP = 3
    QUERYSET_PRODUCTS_COUNT = 12

    def get_queryset(self):
        qs = Product.objects.filter(is_deleted=False).order_by('id').reverse()
        shops = []
        products = []

        for p in qs:
            if shops.count(p.image.post.shop.instagram_username) < self.MAXIMUM_PRODUCTS_FROM_ONE_SHOP:
                shops.append(p.image.post.shop.instagram_username)
                products.append(p)
            if len(products) == self.QUERYSET_PRODUCTS_COUNT:
                break

        return products


class DiscountedProductsView(ListAPIView):
    serializer_class = ProductReadonlySerializer
    permission_classes = [AllowAny]

    MAXIMUM_PRODUCTS_FROM_ONE_SHOP = 3
    QUERYSET_PRODUCTS_COUNT = 10

    def get_queryset(self):
        qs = Product.objects.filter(is_deleted=False).order_by('id').reverse()
        qs = [p for p in qs if p.discount_percent > 0]
        shops = []
        products = []

        for p in qs:
            if shops.count(p.image.post.shop.instagram_username) < self.MAXIMUM_PRODUCTS_FROM_ONE_SHOP:
                shops.append(p.image.post.shop.instagram_username)
                products.append(p)
            if len(products) == self.QUERYSET_PRODUCTS_COUNT:
                break

        return products


class MigrationHelper(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        from order.models import OrderItem
        for item in OrderItem.objects.all():
            item.product_final_price = item.product.final_price
            item.product_original_price = item.product.original_price
            item.product_title = item.product.title
            item.product_discount_percent = item.product.discount_percent
            item.save()
        return Response(status=status.HTTP_200_OK)
