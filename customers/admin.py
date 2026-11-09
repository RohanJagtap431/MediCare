from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "phone",
        "email",
        "city",
        "opening_balance",
        "is_active",
    )

    search_fields = (
        "customer_name",
        "phone",
        "email",
    )

    list_filter = (
        "gender",
        "is_active",
        "state",
        "city",
    )

    list_per_page = 25

    readonly_fields = (
        "created_at",
        "updated_at",
    )