from django.db import models


# Create your models here.
class Product(models.Model):
    # shop = models.ForeignKey(Shop, models.PROTECT)
    title = models.CharField(max_length=100, blank=True)
    instagram_link = models.CharField(max_length=70, blank=True)
    rate = models.PositiveSmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductPrice(models.Model):
    product = models.ForeignKey(Product, models.PROTECT)
    price = models.IntegerField()
    discount = models.SmallIntegerField()
    set_at = models.DateTimeField(auto_now_add=True)

