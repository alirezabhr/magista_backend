from django.contrib import admin

from .models import User, Shop, Customer, Otp

# Register your models here.
admin.site.register(User)
admin.site.register(Shop)
admin.site.register(Customer)
admin.site.register(Otp)
