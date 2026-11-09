from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [

    # Create Bill
    path(
        "create/",
        views.sale_create,
        name="sale_create"
    ),

    # Bill Management
    path(
        "bills/",
        views.bill_list,
        name="bill_list"
    ),

    # Cancel Bill
    path(
        "bills/<int:sale_id>/cancel/",
        views.sale_cancel,
        name="sale_cancel"
    ),

    # Permanent Delete
    path(
        "bills/<int:sale_id>/delete/",
        views.sale_delete,
        name="sale_delete"
    ),

    # Printable Invoice
    path(
        "invoice/<int:sale_id>/",
        views.sale_invoice,
        name="sale_invoice"
    ),
    
    path(
        "bills/<int:sale_id>/payment/",
        views.sale_add_payment,
        name="sale_add_payment",
    ),
]