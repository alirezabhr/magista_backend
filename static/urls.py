from django.urls import path

from . import views

urlpatterns = [
    path('homepage/', views.HomepageImageView.as_view(), name='homepage-image'),
]
