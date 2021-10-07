from django.urls import path

from . import views

urlpatterns = [
    path('<shortcode>/', views.ProductDetailView.as_view()),
]
