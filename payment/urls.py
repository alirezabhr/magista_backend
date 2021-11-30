from django.urls import path

from . import views

urlpatterns = [
    path('ipg/', views.PaymentView.as_view()),
]
