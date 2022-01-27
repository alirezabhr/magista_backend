from django.urls import path

from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('shop/<int:shop_pk>/', views.ShopOrdersView.as_view(), name='shop-orders'),    # vendor
    path('customer/<int:customer_pk>/', views.CustomerOrdersView.as_view(), name='customer-orders'),
    path('invoice/<int:invoice_pk>/', views.InvoiceView.as_view()),
    path('<int:order_pk>/', views.OrderView.as_view()),
    path('<int:order_pk>/rate/', views.OrderRateView.as_view()),
    path('<int:order_pk>/discount/apply/', views.ApplyShopDiscountView.as_view()),     # for customer
    path('shop/<int:shop_pk>/stats/', views.ShopStatsView.as_view(), name='shop-stats'),
]
