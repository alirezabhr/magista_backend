from django.utils import timezone

from django.db import models

from order.models import Order, OrderItem
from payment.models import Withdraw
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
    commission_percent = models.SmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def rate(self):
        rate_sum = 0
        count = 0
        for product in Product.objects.filter(image__post__shop=self):
            if product.rate:
                count += 1
                rate_sum += product.rate
        return rate_sum

    @property
    def remaining_amount(self):
        days = 2
        return self.total_orders_price_before_n_days(days) - self.total_withdraw()

    def withdrawal_amount(self):
        return (self.remaining_amount * (100 - self.commission_percent)) // 100

    def total_orders_price_before_n_days(self, n_days):
        """ returns total price of paid orders in this shop which created before last n days """
        now = timezone.now()
        delta = timezone.timedelta(days=n_days)
        date_time_range = (self.created_at, now - delta)
        order_status_range = (Order.Status.SHIPPED, Order.Status.RECEIVED)
        order_query = Order.objects.filter(shop=self, status__range=order_status_range,
                                           invoice__created_at__range=date_time_range)
        amount = 0
        for order in order_query:
            amount += order.total_price
        return amount

    def total_withdraw(self):
        """ returns total withdraw with this shop """
        now = timezone.now()
        date_time_range = (self.created_at, now)
        withdraw_query = Withdraw.objects.filter(shop=self, paid_at__range=date_time_range)

        amount = 0
        for withdraw in withdraw_query:
            amount += withdraw.amount_without_commission
        return amount

    def __str__(self):
        return f'{self.id}: {self.vendor.username} | {self.instagram_username}'


class BankCredit(models.Model):
    shop = models.ForeignKey(Shop, models.CASCADE)
    sheba = models.CharField(max_length=30)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)

    def __str__(self):
        return f'{self.id}(shop: {self.shop.instagram_username} | {self.sheba})'


class Post(models.Model):
    shop = models.ForeignKey(Shop, models.PROTECT)
    shortcode = models.CharField(max_length=15)  # this shortcode can create by backend
    description = models.TextField(blank=True)
    instagram_link = models.CharField(max_length=70, blank=True)  # instagram shortcode
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_product(self):
        return Product.objects.filter(image__post=self, is_deleted=False).exists()

    @property
    def product_images(self):
        return ProductImage.objects.filter(post=self)

    def __str__(self):
        return f"{self.pk}: {self.shop.instagram_username} | {self.shortcode}"


class ProductImage(models.Model):
    post = models.ForeignKey(Post, models.PROTECT)
    display_image = models.CharField(max_length=120, null=True)

    @property
    def products(self):
        return Product.objects.filter(image=self, is_deleted=False)


class Product(models.Model):
    image = models.ForeignKey(ProductImage, models.PROTECT)
    title = models.CharField(max_length=40, blank=True)
    description = models.CharField(max_length=60, blank=True)
    original_price = models.PositiveIntegerField()
    is_existing = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def attributes(self):
        return ProductAttribute.objects.filter(product=self)

    @property
    def rate(self):
        sum_ = 0
        index = -1

        for index, oi in enumerate(OrderItem.objects.filter(product=self)):
            if oi.order.rate:
                sum_ += oi.order.rate

        if index == -1:
            return None
        return float("{:.1f}".format(sum_ / (index + 1)))

    @property
    def discount_percent(self):
        discount = Discount.objects.filter(product=self, is_active=True).last()
        if discount is None or discount.is_active is False:
            return 0
        return discount.percent

    @property
    def discount_amount(self):
        discount = Discount.objects.filter(product=self).last()
        if discount is None or discount.is_active is False:
            return 0
        return discount.amount

    @property
    def discount_description(self):
        discount = Discount.objects.filter(product=self).last()
        if discount is None or discount.is_active is False:
            return ''
        return discount.description

    @property
    def final_price(self):
        return self.original_price - self.discount_amount

    @property
    def tag(self):
        return TagLocation.objects.get(product=self)

    def __str__(self):
        return f"{self.pk}: {self.image.post.shop.instagram_username} - {self.title}"


class TagLocation(models.Model):
    product = models.OneToOneField(Product, models.CASCADE)
    x = models.SmallIntegerField(default=50)
    y = models.SmallIntegerField(default=50)


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
