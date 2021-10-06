from django.db import models


# Create your models here.
class Product(models.Model):
    # shop = models.ForeignKey(Shop, models.PROTECT)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    instagram_link = models.CharField(max_length=70, blank=True)
    rate = models.PositiveSmallIntegerField()
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


class Order(models.Model):
    # payer = models.ForeignKey(User, models.PROTECT)
    status = models.SmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product_price = models.ForeignKey(ProductPrice, models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
