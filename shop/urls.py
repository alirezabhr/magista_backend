from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.ShopView.as_view(), name='create-shop'),   # for vendor
    path('<int:pk>/products/', views.ShopProductsView.as_view()),    # for vendor
    path('<str:ig_username>/products/', views.ShopProductsPreviewView.as_view()),    # for customer
    path('preview/<str:ig_username>/', views.ShopPreview.as_view(), name='shop-preview'),    # for customer
]
