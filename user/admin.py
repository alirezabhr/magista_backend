from django.contrib import admin

from .models import User, Shop, Customer

# Register your models here.
admin.site.register(User)
admin.site.register(Shop)
admin.site.register(Customer)
