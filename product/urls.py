from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ShopProductsView.as_view()),
    path('<shortcode>/', views.ProductDetailView.as_view()),
]
