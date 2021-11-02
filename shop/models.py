from django.db import models

from user.models import User, Customer


# Create your models here.
class Shop(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    instagram_username = models.CharField(max_length=30, unique=True)
    instagram_id = models.IntegerField(unique=True)
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address = models.TextField()
    profile_pic = models.CharField(max_length=80, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}: {self.vendor.username} | {self.instagram_username}'


class Product(models.Model):
    shop = models.ForeignKey(Shop, models.PROTECT)
    shortcode = models.CharField(max_length=15)     # this shortcode can create by backend
    display_image = models.CharField(max_length=120, null=True)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    instagram_link = models.CharField(max_length=70, blank=True)    # instagram shortcode
    rate = models.PositiveSmallIntegerField(null=True)
    is_existing = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}: {self.shop} - {self.title}"


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, models.PROTECT)
    price = models.IntegerField()
    set_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}: ({self.price}) {self.product.shop} - {self.product.title}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=50)


class Discount(models.Model):
    product = models.ForeignKey(Product, models.PROTECT, null=True)
    percent = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    disabled_at = models.DateTimeField(null=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, models.PROTECT)
    status = models.SmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product_price = models.ForeignKey(ProductPrice, models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
