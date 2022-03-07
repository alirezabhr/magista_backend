from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import HomepageImage
from .serializers import HomepageImageSerializer


# Create your views here.
class HomepageImageView(ListAPIView):
    serializer_class = HomepageImageSerializer
    queryset = HomepageImage.objects.filter(active=True).order_by('id')
    permission_classes = [AllowAny]
