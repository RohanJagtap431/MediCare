
from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("stock/", views.stock_list, name="stock_list"),
    path("expiry/", views.expiry_list, name="expiry_list"),
]
