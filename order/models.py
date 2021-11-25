from django.db import models

from shop.models import Shop, Product
from user.models import Customer


# Create your models here.
class IPGPayment(models.Model):
    customer = models.ForeignKey(Customer, models.PROTECT)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def orders(self):
        return Order.objects.filter(ipg_payment=self)


class Order(models.Model):
    class Status(models.IntegerChoices):
        AWAITING_PAYMENT = 1
        PAID = 2
        SHIPPED = 3
        RECEIVED = 4
        CANCELED = 5

    ipg_payment = models.ForeignKey(IPGPayment, models.PROTECT)
    shop = models.ForeignKey(Shop, models.PROTECT)
    status = models.IntegerField(choices=Status.choices)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def order_items(self):
        return OrderItem.objects.filter(order=self)

    @property
    def customer(self):
        return self.ipg_payment.customer

    @property
    def total_price(self):
        total = 0
        for item in self.order_items:
            total += item.price * item.count
        return total

    def __str__(self):
        return f"id: {self.pk} | {self.created_at} | status: {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product = models.ForeignKey(Product, models.PROTECT)
    price = models.PositiveIntegerField()
    count = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"id: {self.pk} | order: {self.order.pk}"
