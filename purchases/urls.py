from django.urls import path
from . import views

app_name = "purchases"

urlpatterns = [
    path("", views.purchase_list, name="purchase_list"),

    path("add/", views.purchase_create, name="purchase_create"),
    path("<int:pk>/", views.purchase_detail, name="purchase_detail"),
    
    path(
        "<int:pk>/receive/",
        views.purchase_receive,
        name="purchase_receive"
    ),
    
    path(
        "<int:pk>/payment/add/",
        views.purchase_add_payment,
        name="purchase_add_payment"
    ),
]