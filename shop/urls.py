from django.urls import path

from . import views

urlpatterns = [
    path('media-query/', views.ShopMediaQueryView.as_view(), name='get-user-ig-media'),
    path('<int:vendor_pk>/', views.ShopView.as_view(), name='create-shop'),   # for vendor
    path('<int:shop_pk>/post/', views.ShopPostView.as_view()),    # for vendor
    path('<int:shop_pk>/bank-credit/', views.ShopBankCreditsView.as_view()),    # for vendor
    path('<str:ig_username>/post/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('<str:ig_username>/preview/', views.ShopPublicView.as_view(), name='shop-preview'),    # for customer
    path('post/<str:post_shortcode>/preview/', views.PostPublicView.as_view()),    # for customer and vendor
    path('product/<int:product_pk>/', views.ProductView.as_view()),    # for vendor
    path('product/<int:product_pk>/discount/', views.ProductDiscountView.as_view()),     # for vendor
    path('product/<int:product_pk>/attribute/', views.ProductAttributeCreateView.as_view()),     # for vendor
    path('product/<int:product_pk>/attribute/<int:pk>/', views.ProductAttributeDeleteView.as_view()),     # for vendor
]
