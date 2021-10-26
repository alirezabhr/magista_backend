from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# Managers
class CustomUserManager(UserManager):
    def create_superuser(self, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if phone is None:
            raise TypeError('Superuser must have phone number')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username=phone, phone=phone, email=email, password=password, **extra_fields)

    def create_user(self, phone, password=None, **extra_fields):
        if phone is None:
            raise TypeError('users must have a phone number.')
        seller = User(username=phone, phone=phone, **extra_fields)
        seller.set_password(password)
        seller.save()
        return seller


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=11, unique=True)     # 09171231122

    objects = CustomUserManager()
    USERNAME_FIELD = 'phone'

    def __str__(self):
        return f'{self.id}: {self.username}'


class Shop(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    instagram_username = models.CharField(max_length=30, unique=True)
    instagram_id = models.IntegerField(unique=True)
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    profile_pic = models.CharField(max_length=80, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}: {self.vendor.username} | {self.instagram_id}'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address = models.TextField(null=True)

    def __str__(self):
        return f'{self.id}: {self.user.username}'


class Otp(models.Model):
    phone = models.CharField(max_length=11)
    otp_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}: {self.phone}'
