from django.urls import path

from . import views

urlpatterns = [
    path('media-query/', views.ShopMediaQueryView.as_view(), name='get-user-ig-media'),
    path('<int:vendor_pk>/', views.ShopView.as_view(), name='create-shop'),   # for vendor
    path('<int:shop_pk>/products/', views.ShopProductsView.as_view()),    # for vendor
    path('<str:ig_username>/products/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('<str:ig_username>/preview/', views.ShopPreviewView.as_view(), name='shop-preview'),    # for customer
    path('product/<str:product_shortcode>/', views.ProductView.as_view()),    # for vendor
    path('product/<str:product_shortcode>/preview/', views.ProductPreviewView.as_view()),    # for customer
    path('product/<str:product_shortcode>/discount/', views.ProductDiscountView.as_view()),
]
