from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', views.UserView.as_view(), name='user-detail'),
    path('send-otp/', views.send_otp_view, name='send-otp'),
    path('check-otp/', views.check_otp_view, name='check-otp'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('customer/', views.CustomerView.as_view(), name='create-customer'),
]
