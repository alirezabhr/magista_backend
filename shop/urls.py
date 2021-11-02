from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ShopProductsView.as_view()),    # for vendor
    path('shop/<str:ig_username>/products/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('<shortcode>/', views.ProductDetailView.as_view()),
]
