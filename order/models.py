from django.db import models

from user.models import Customer


# Create your models here.
class Invoice(models.Model):
    customer = models.ForeignKey(Customer, models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def orders(self):
        return Order.objects.filter(invoice=self)

    @property
    def total_amount(self):
        total = 0
        for order in self.orders:
            total += order.total_price
        return total

    @property
    def is_paid(self):
        return self.orders.last().status >= Order.Status.PAID


class Order(models.Model):
    status_text_list = ['در انتظار پرداخت', 'پرداخت شده', 'تایید شده', 'ارسال شده', 'دریافت شده', 'لغو شده']

    class Status(models.IntegerChoices):
        AWAITING_PAYMENT = 1
        PAID = 2
        VERIFIED = 3
        SHIPPED = 4
        RECEIVED = 5
        CANCELED = 6

    invoice = models.ForeignKey(Invoice, models.PROTECT)
    shop = models.ForeignKey('shop.Shop', models.PROTECT)
    status = models.IntegerField(choices=Status.choices)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def created_at(self):
        return self.invoice.created_at

    @property
    def order_items(self):
        return OrderItem.objects.filter(order=self)

    @property
    def customer(self):
        return self.invoice.customer

    @property
    def total_price(self):
        total = 0
        for item in self.order_items:
            total += item.price * item.count
        return total

    @property
    def status_text(self):
        return self.status_text_list[self.status - 1]

    def __str__(self):
        return f"id: {self.pk} | {self.created_at} | status: {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product = models.ForeignKey('shop.Product', models.PROTECT)
    price = models.PositiveIntegerField()
    count = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"id: {self.pk} | order: {self.order.pk}"
