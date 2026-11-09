
from django.urls import path
from . import views

app_name = "medicines"

urlpatterns = [
    # Category URLs
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),

    # Manufacturer URLs
    path("manufacturers/", views.manufacturer_list, name="manufacturer_list"),
    path("manufacturers/add/", views.manufacturer_create, name="manufacturer_create"),
    path("manufacturers/<int:pk>/edit/", views.manufacturer_update, name="manufacturer_update"),
    path("manufacturers/<int:pk>/delete/", views.manufacturer_delete, name="manufacturer_delete"),
    
    path(
        "manufacturers/<int:pk>/toggle-status/",
        views.manufacturer_toggle_status,
        name="manufacturer_toggle_status"
    ),
    
    path(
        "categories/<int:pk>/toggle-status/",
        views.category_toggle_status,
        name="category_toggle_status"
    ),
    
    # MEDICINE MANAGEMENT

    path("medicines/", views.medicine_list, name="medicine_list"),

    path("medicines/add/", views.medicine_create, name="medicine_create"),

    path("medicines/<int:pk>/edit/", views.medicine_update, name="medicine_update"),

    path("medicines/<int:pk>/delete/", views.medicine_delete, name="medicine_delete"),

    path("medicines/<int:pk>/toggle-status/", views.medicine_toggle_status, name="medicine_toggle_status"),
    
    path("batches/", views.batch_list, name="batch_list"),

    path("batches/add/", views.batch_create, name="batch_create"),

    path("batches/<int:pk>/edit/", views.batch_update, name="batch_update"),

    path("batches/<int:pk>/delete/", views.batch_delete, name="batch_delete"),
]
