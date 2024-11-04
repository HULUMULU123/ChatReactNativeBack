from django.urls import path
from . import views

urlpatterns = [
    path('signin/', views.SignView.as_view(), name='signin'), 
]