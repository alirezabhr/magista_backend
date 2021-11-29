from django.urls import path

from . import views

urlpatterns = [
    path('', views.IssueView.as_view(), name='log issue'),
]
