from django.db import models


# Create your models here.
class Product(models.Model):
    # shop = models.ForeignKey(Shop, models.PROTECT)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    instagram_link = models.CharField(max_length=70, blank=True)
    rate = models.PositiveSmallIntegerField()
    is_existing = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, models.PROTECT)
    price = models.IntegerField()
    set_at = models.DateTimeField(auto_now_add=True)


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
    # payer = models.ForeignKey(User, models.PROTECT)
    status = models.SmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product_price = models.ForeignKey(ProductPrice, models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
