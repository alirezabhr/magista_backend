from django.urls import path

from . import views

urlpatterns = [
    path('media-query/', views.ShopMediaQueryView.as_view(), name='get-user-ig-media'),
    path('<int:vendor_pk>/', views.ShopView.as_view(), name='create-shop'),   # for vendor
    path('<int:shop_pk>/product/', views.ShopProductsView.as_view()),    # for vendor
    path('<int:shop_pk>/bank-credit/', views.ShopBankCreditsView.as_view()),    # for vendor
    path('<str:ig_username>/product/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('<str:ig_username>/preview/', views.ShopPublicView.as_view(), name='shop-preview'),    # for customer
    path('product/<str:product_shortcode>/', views.ProductView.as_view()),    # for vendor
    path('product/<str:product_shortcode>/preview/', views.ProductPublicView.as_view()),    # for customer
    path('product/<str:product_shortcode>/discount/', views.ProductDiscountView.as_view()),     # for vendor
    path('product/<str:product_shortcode>/attribute/', views.ProductAttributeCreateView.as_view()),     # for vendor
    path('product/<str:product_shortcode>/attribute/<int:pk>/', views.ProductAttributeDeleteView.as_view()),     # for vendor
]
