from django.utils import timezone

from django.db import models

from order.models import Order
from user.models import User


# Create your models here.
class Shop(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    instagram_username = models.CharField(max_length=30, unique=True)
    instagram_id = models.BigIntegerField(unique=True)
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address = models.TextField()
    wallet = models.IntegerField(default=0)  # Toman
    profile_pic = models.CharField(max_length=80, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def rate(self):
        rate_sum = 0
        count = 0
        for product in Product.objects.filter(shop=self):
            if product.rate:
                count += 1
                rate_sum += product.rate
        return rate_sum

    @property
    def withdrawal_amount(self):
        return self.wallet - self.before_n_days_orders_price(2)     # orders before last 2 days

    def before_n_days_orders_price(self, n_days):
        """ returns paid orders of this shop which created in last n days """
        now = timezone.now()
        delta = timezone.timedelta(days=n_days)
        date_time_range = (self.created_at, now-delta)
        order_status_range = (Order.Status.SHIPPED, Order.Status.RECEIVED)
        order_query = Order.objects.filter(shop=self, status__range=order_status_range, invoice__created_at__range=date_time_range)
        amount = 0
        for order in order_query:
            amount += order.total_price
        return amount

    def __str__(self):
        return f'{self.id}: {self.vendor.username} | {self.instagram_username}'


class BankCredit(models.Model):
    shop = models.ForeignKey(Shop, models.CASCADE)
    sheba = models.CharField(max_length=30)
    full_name = models.CharField(max_length=60)


class Product(models.Model):
    shop = models.ForeignKey(Shop, models.PROTECT)
    shortcode = models.CharField(max_length=15)     # this shortcode can create by backend
    display_image = models.CharField(max_length=120, null=True)
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    instagram_link = models.CharField(max_length=70, blank=True)    # instagram shortcode
    rate = models.PositiveSmallIntegerField(null=True)
    original_price = models.PositiveIntegerField(null=True, default=None)
    is_existing = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def attributes(self):
        return ProductAttribute.objects.filter(product=self)

    @property
    def discount_percent(self):
        discount = Discount.objects.filter(product=self, is_active=True).last()
        if discount is None:
            return 0
        return discount.percent

    @property
    def discount_amount(self):
        discount = Discount.objects.filter(product=self, is_active=True).last()
        if discount is None:
            return 0
        return discount.amount

    @property
    def discount_description(self):
        discount = Discount.objects.filter(product=self, is_active=True).last()
        if discount is None:
            return ''
        return discount.description

    @property
    def final_price(self):
        if self.original_price:
            return self.original_price - self.discount_amount
        return None

    def __str__(self):
        return f"{self.pk}: {self.shop} - {self.title}"


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, models.CASCADE)
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=50)


class Discount(models.Model):
    product = models.ForeignKey(Product, models.PROTECT, null=True)
    percent = models.PositiveSmallIntegerField()
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    # start_at = models.DateTimeField()
    # end_at = models.DateTimeField(null=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # disabled_at = models.DateTimeField(null=True)
