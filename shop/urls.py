from django.urls import path

from . import views

urlpatterns = [
    path('request/', views.ShopCreationRequestView.as_view(), name='shop-creation-request'),
    path('media-query/', views.ShopMediaQueryView.as_view(), name='get-user-ig-media'),
    path('media-query/new-posts/', views.ShopMediaQueryNewPostsView.as_view()),
    path('save-media/', views.SaveMediaView.as_view(), name='save-media'),
    path('<int:vendor_pk>/', views.ShopView.as_view(), name='create-shop'),   # for vendor
    # inflation endpoint is for vendors (increases price on all products)
    path('<int:shop_pk>/bio/', views.ShopBioView.as_view(), name='shop-bio'),
    path('<int:shop_pk>/inflation/', views.ShopInflationView.as_view(), name='shop-inflation'),
    path('<int:shop_pk>/discount/', views.ShopDiscountView.as_view()),     # for vendor
    path('<int:shop_pk>/post/', views.ShopPostView.as_view(), name='create-all-posts'),    # for vendor
    path('<int:shop_pk>/post/new-posts/', views.ShopNewPostView.as_view(), name='create-new-posts'),    # for vendor
    path('<int:shop_pk>/bank-credit/', views.ShopBankCreditsView.as_view()),    # for vendor
    path('<str:ig_username>/post/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('<str:ig_username>/preview/', views.ShopPublicView.as_view(), name='shop-preview'),    # for customer
    path('post/<str:post_shortcode>/preview/', views.PostPublicView.as_view()),    # for customer and vendor
    path('post/<str:post_shortcode>/product-images/', views.PostProductImagesPublicView.as_view()),    # for customer and vendor
    path('post/<str:post_shortcode>/', views.PostEditView.as_view()),    # for vendor
    path('product/', views.ShopProductView.as_view(), name='create-product'),    # for vendor
    path('product/tag/', views.ProductTagView.as_view()),    # for vendor
    path('product/<int:product_pk>/', views.ProductView.as_view()),    # for vendor
    path('product/<int:product_pk>/discount/', views.ProductDiscountView.as_view()),     # for vendor
    path('product/<int:product_pk>/attribute/', views.ProductAttributeCreateView.as_view()),     # for vendor
    path('product/<int:product_pk>/attribute/<int:pk>/', views.ProductAttributeDeleteView.as_view()),     # for vendor
]
