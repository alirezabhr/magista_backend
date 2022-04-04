from django.utils import timezone

from django.db import models

from order.models import Order, OrderItem
from payment.models import Withdraw
from user.models import User


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return f'{self.id}: {self.name}'


class ShopCreationStep(models.Model):
    REQUESTED = 'REQUESTED'
    VERIFIED = 'VERIFIED'
    FORM_SUBMITTED = 'SUBMITTED'
    CREATED = 'CREATED'

    STEP_CHOICES = (
        (REQUESTED, 'Requested'),
        (VERIFIED, 'Verified'),
        (FORM_SUBMITTED, 'Submitted'),
        (CREATED, 'Created'),
    )

    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applicant')
    instagram_username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True)
    step = models.CharField(max_length=10, choices=STEP_CHOICES, default=REQUESTED)

    def __str__(self):
        return self.instagram_username


class Shop(models.Model):
    class PreparationTime(models.IntegerChoices):
        TWO_HOURS = 0
        TWELVE_HOURS = 1
        ONE_DAY = 2
        THREE_DAYS = 3
        ONE_WEEK = 4

    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_vendor')
    email = models.EmailField(blank=True)
    instagram_username = models.CharField(max_length=30, unique=True)
    instagram_id = models.BigIntegerField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='shop_category')
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address = models.TextField()
    bio = models.CharField(max_length=400, blank=True)
    preparation = models.IntegerField(choices=PreparationTime.choices)
    profile_pic = models.CharField(max_length=80, null=True)
    commission_percent = models.SmallIntegerField(default=5)
    last_scrape = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def delivery(self):
        return Shipment.objects.get(shop=self)

    @property
    def rate(self):
        rate_sum = 0
        count = 0
        for product in Product.objects.filter(image__post__shop=self):
            if product.rate:
                count += 1
                rate_sum += product.rate
        if count:
            return float("{:.1f}".format(rate_sum / count))
        return 0

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
            amount += order.final_price
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


class Shipment(models.Model):
    class FreeDelivery(models.IntegerChoices):
        NOT_FREE = 0
        OCCASIONALLY_FREE = 1
        TOTALLY_FREE = 2

    shop = models.OneToOneField(Shop, models.CASCADE, related_name='shop_shipment')
    send_everywhere = models.BooleanField()     # true: entire country, false: only in city
    has_national_post = models.BooleanField()
    has_online_delivery = models.BooleanField()
    city_cost = models.IntegerField(choices=FreeDelivery.choices)
    country_cost = models.IntegerField(choices=FreeDelivery.choices, null=True)     # null = send_everywhere is false

    @property
    def national_post(self):
        # None: this shop won't send by national post
        if self.has_national_post:
            return DeliveryPrice.objects.get(shipment=self, type=DeliveryPrice.DeliveryType.NATIONAL_POST)
        return None

    @property
    def online_delivery(self):
        # None: this shop won't send by online delivery
        if self.has_online_delivery:
            return DeliveryPrice.objects.get(shipment=self, type=DeliveryPrice.DeliveryType.ONLINE_DELIVERY)
        return None

    @property
    def city_free_cost_from(self):
        # None: this shop doesn't have free delivery in city
        if self.city_cost == self.FreeDelivery.OCCASIONALLY_FREE:
            return OccasionallyFreeDelivery.objects.get(shipment=self, type=OccasionallyFreeDelivery.AreaType.CITY)
        return None

    @property
    def country_free_cost_from(self):
        # None: this shop doesn't have free delivery in country
        if self.country_cost == self.FreeDelivery.OCCASIONALLY_FREE:
            return OccasionallyFreeDelivery.objects.get(shipment=self, type=OccasionallyFreeDelivery.AreaType.COUNTRY)
        return None

    def __str__(self):
        return f'{self.id}=> shop: {self.shop.instagram_username}'


class DeliveryPrice(models.Model):
    class DeliveryType(models.IntegerChoices):
        NATIONAL_POST = 0
        ONLINE_DELIVERY = 1

    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT, related_name='delivery_price_shipment')
    type = models.IntegerField(choices=DeliveryType.choices)
    base = models.PositiveIntegerField()
    per_kilo = models.PositiveIntegerField()

    class Meta:
        unique_together = ('shipment', 'type')

    def __str__(self):
        return f'{self.id}=> shipment: {self.shipment.id} | shop: {self.shipment.shop.instagram_username}'


class OccasionallyFreeDelivery(models.Model):
    class AreaType(models.IntegerChoices):
        CITY = 0
        COUNTRY = 1

    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT, related_name='occasionally_free_shipment')
    type = models.IntegerField(choices=AreaType.choices)
    free_from = models.PositiveIntegerField()

    class Meta:
        unique_together = ('shipment', 'type')

    def __str__(self):
        return f'{self.id}=> shipment: {self.shipment.id} | shop: {self.shipment.shop.instagram_username}'


class BankCredit(models.Model):
    shop = models.ForeignKey(Shop, models.CASCADE, related_name='shop_credit_cards')
    sheba = models.CharField(max_length=30)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)

    def __str__(self):
        return f'{self.id}(shop: {self.shop.instagram_username} | {self.sheba})'


class Post(models.Model):
    shop = models.ForeignKey(Shop, models.PROTECT, related_name='shop_posts')
    shortcode = models.CharField(max_length=25)  # this shortcode can create by backend
    description = models.TextField(blank=True)
    instagram_link = models.CharField(max_length=70, blank=True)  # instagram shortcode
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def has_product(self):
        return Product.objects.filter(image__post=self, is_deleted=False).exists()

    @property
    def preview_image(self):
        return ProductImage.objects.filter(post=self).first().display_image

    def __str__(self):
        return f"{self.pk}: {self.shop.instagram_username} | {self.shortcode}"


class ProductImage(models.Model):
    post = models.ForeignKey(Post, models.PROTECT, related_name='post_product_images')
    display_image = models.CharField(max_length=120, null=True)

    @property
    def products(self):
        return Product.objects.filter(image=self, is_deleted=False)


class Product(models.Model):
    image = models.ForeignKey(ProductImage, models.PROTECT, related_name='product_image_products')
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
        discount = ProductDiscount.objects.filter(product=self).last()
        if discount is None or discount.is_active is False:
            return 0
        return discount.percent

    @property
    def discount_amount(self):
        if self.discount_percent:
            return self.original_price - ((self.original_price * (100 - self.discount_percent)) // 100)
        return 0

    @property
    def discount_description(self):
        discount = ProductDiscount.objects.filter(product=self).last()
        if discount is None or discount.is_active is False:
            return ''
        return discount.description

    @property
    def final_price(self):
        return self.original_price - self.discount_amount

    @property
    def tag(self):
        return TagLocation.objects.get(product=self)

    @property
    def post_shortcode(self):
        return self.image.post.shortcode

    def __str__(self):
        return f"{self.pk}: {self.image.post.shop.instagram_username} - {self.title}"


class TagLocation(models.Model):
    product = models.OneToOneField(Product, models.CASCADE, related_name='product_tag')
    x = models.SmallIntegerField(default=50)
    y = models.SmallIntegerField(default=50)


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name='product_attributes')
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=50)


class ProductDiscount(models.Model):
    product = models.ForeignKey(Product, models.PROTECT, null=True, related_name='product_discount')
    percent = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)


class ShopDiscount(models.Model):
    shop = models.ForeignKey(Shop, models.PROTECT, related_name='shop_discount')
    percent = models.PositiveSmallIntegerField()
    description = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    code = models.CharField(max_length=10)
    count = models.IntegerField(null=True)  # count == null means this discount doesn't have limit
    start_at = models.DateTimeField(null=True)
    finish_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
