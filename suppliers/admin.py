from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "supplier_name",
        "contact_person",
        "phone",
        "city",
        "gstin",
        "opening_balance",
        "is_active",
    )

    search_fields = (
        "supplier_name",
        "contact_person",
        "phone",
        "gstin",
    )

    list_filter = (
        "is_active",
        "state",
        "city",
    )

    list_per_page = 25