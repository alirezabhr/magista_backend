from rest_framework import serializers

from .models import User, Shop


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "password",
            "phone",
            "instagram_id",
            "province",
            "city"
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'
