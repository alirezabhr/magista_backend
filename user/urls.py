from django.urls import path

from . import views

urlpatterns = [
    path('otp/', views.OtpView.as_view()),
    path('check-otp/', views.check_otp),
    path('signup/', views.UserSignupView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('shop/', views.ShopView.as_view()),
    path('customer/', views.CustomerView.as_view()),
    path('user-media/', views.UserMediaView.as_view())
]
