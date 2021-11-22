from django.db import models

from shop.models import Shop, Product
from user.models import Customer


# Create your models here.
class Invoice(models.Model):
    class Status(models.IntegerChoices):
        AWAITING_PAYMENT = 1
        PAID = 2
        SHIPPED = 3
        RECEIVED = 4
        CANCELED = 5

    shop = models.ForeignKey(Shop, models.PROTECT)
    customer = models.ForeignKey(Customer, models.PROTECT)
    status = models.IntegerField(choices=Status.choices)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.pk} | {self.created_at} | status: {self.status}"


class OrderItem(models.Model):
    invoice = models.ForeignKey(Invoice, models.PROTECT)
    product = models.ForeignKey(Product, models.PROTECT)
    price = models.PositiveIntegerField()
    count = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"id: {self.pk} | invoice: {self.invoice.pk}"

