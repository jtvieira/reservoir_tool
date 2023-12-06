# res_view/urls.py

from django.urls import path
from res_view import views

urlpatterns = [
    path("", views.home, name='home'),
    path("get_info/", views.get_info, name='get_info'),
]
