from django.urls import path

from . import views

urlpatterns = [
    path('user/', views.UserView.as_view(), name='user-detail'),
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('check-otp/', views.check_otp_view, name='check-otp'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('customer/', views.CustomerView.as_view(), name='create-customer'),
    path('user-media/', views.UserMediaView.as_view(), name='get-user-ig-media'),
]
