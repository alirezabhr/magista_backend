from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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

    def get_queryset(self):
        products = Product.objects.all().order_by('id').reverse()
        return products[:10]


class DiscountedProductsView(ListAPIView):
    serializer_class = ProductReadonlySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        products = Product.objects.filter(discount__amount__gt=0).order_by('id').reverse()
        if products.count() > 10:
            return products[:10]
        return products
