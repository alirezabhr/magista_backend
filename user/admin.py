from django.contrib import admin

from .models import User, Customer, Otp

# Register your models here.
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Otp)
