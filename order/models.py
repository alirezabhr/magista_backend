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
            total += order.final_price
        return total

    @property
    def is_paid(self):
        return self.orders.last().paid_at is not None


class Order(models.Model):
    status_text_list = ['در انتظار پرداخت', 'پرداخت شده', 'تایید شده', 'ارسال شده', 'دریافت شده', 'لغو شده']

    class Status(models.IntegerChoices):
        AWAITING_PAYMENT = 0
        PAID = 1
        VERIFIED = 2
        SHIPPED = 3
        RECEIVED = 4
        CANCELED = 5

    invoice = models.ForeignKey(Invoice, models.PROTECT)
    shop = models.ForeignKey('shop.Shop', models.PROTECT)
    status = models.IntegerField(choices=Status.choices)
    rate = models.SmallIntegerField(null=True)
    paid_at = models.DateTimeField(null=True)
    verified_at = models.DateTimeField(null=True)
    shipped_at = models.DateTimeField(null=True)
    canceled_at = models.DateTimeField(null=True)

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
    def has_discount_code(self):
        return OrderShopDiscount.objects.filter(order=self).exists()

    @property
    def total_order_items_original_prices(self):
        total = 0
        for item in self.order_items:
            total += item.product_original_price * item.count
        return total

    def total_order_items_final_prices(self):
        total = 0
        for item in self.order_items:
            total += item.product_final_price * item.count
        return total

    def total_order_items_discount_amount(self):
        return self.total_order_items_original_prices - self.total_order_items_final_prices()

    def shop_discount_amount(self):
        order_shop_discount = OrderShopDiscount.objects.filter(order=self).last()  # just consider the last one
        if order_shop_discount:
            return (self.total_order_items_final_prices() * order_shop_discount.shop_discount.percent) // 100
        else:
            return 0

    @property
    def delivery(self):
        return OrderDeliveryPrice.objects.filter(order=self).last()

    @property
    def delivery_cost(self):
        delivery = self.delivery
        if delivery is not None:
            return delivery.base
        return 0

    @property
    def total_discount_amount(self):
        return self.shop_discount_amount() + self.total_order_items_discount_amount()

    @property
    def final_price(self):
        return self.total_order_items_original_prices - self.total_discount_amount + self.delivery_cost

    @property
    def status_text(self):
        return self.status_text_list[self.status]

    def __str__(self):
        return f"id: {self.pk} | {self.created_at} | status: {self.status_text}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product = models.ForeignKey('shop.Product', models.PROTECT)
    product_title = models.CharField(max_length=40)
    product_original_price = models.PositiveIntegerField()
    product_final_price = models.PositiveIntegerField()
    product_discount_percent = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"id: {self.id} | order: {self.order.id}"


class OrderShopDiscount(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    shop_discount = models.ForeignKey('shop.ShopDiscount', models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.id} | order: {self.order.id} | code: {self.shop_discount.code}"


class OrderDeliveryPrice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, unique=True)
    delivery_id = models.IntegerField()    # like foreign key
    type = models.IntegerField()
    base = models.PositiveIntegerField()
    per_kilo = models.PositiveIntegerField()
    destination_province = models.CharField(max_length=30)
    destination_city = models.CharField(max_length=30)
    destination_address = models.TextField()    # address + postal code

    def __str__(self):
        return f'{self.id}=> shop: {self.order.shop.instagram_username}'
