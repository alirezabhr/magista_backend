from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


# Managers
class CustomUserManager(UserManager):
    def create_superuser(self, phone, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if phone is None:
            raise TypeError('Superuser must have username')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username=phone, phone=phone, email=email, password=password, **extra_fields)

    def create_user(self, phone, password=None, **extra_fields):
        if phone is None:
            raise TypeError('Seller users must have a phone number.')
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
        return self.username
