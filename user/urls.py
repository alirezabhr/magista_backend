from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.SignupUserView.as_view()),
    path('shop/', views.ShopView.as_view()),
    path('customer/', views.CustomerView.as_view()),
]
