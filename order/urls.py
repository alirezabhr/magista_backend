from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('shop/<int:shop_pk>/', views.ShopInvoicesView.as_view(), name='shop-invoices'),
    path('customer/<int:customer_pk>/', views.CustomerOrdersView.as_view(), name='customer-orders'),
]
