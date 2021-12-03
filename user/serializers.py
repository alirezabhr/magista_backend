from rest_framework import serializers

from .models import User, Customer, Otp


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    customer = CustomerSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "password",
            "customer",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class OtpSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Otp
        fields = '__all__'


class UserPhoneSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=11)

    class Meta:
        fields = ['phone']
        model = User
