from rest_framework import serializers

from .models import HomepageImage


class HomepageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageImage
        fields = '__all__'
