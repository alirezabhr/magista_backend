from django.urls import path

from . import views

urlpatterns = [
    path('user/', views.UserView.as_view()),
    path('send-otp/', views.send_otp_view),
    path('check-otp/', views.check_otp_view),
    path('signup/', views.UserSignupView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('shop/', views.ShopView.as_view()),
    path('customer/', views.CustomerView.as_view()),
    path('user-media/', views.UserMediaView.as_view())
]
