from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


# Create your views here.
class ProductDetailView(APIView):
    serializer_class = ProductSerializer

    def get(self, request, shortcode):
        product = get_object_or_404(Product, shortcode=shortcode)
        ser = self.serializer_class(product)
        return Response(ser.data, status=status.HTTP_200_OK)
