from django.contrib import admin
from .models import ShopProfile


@admin.register(ShopProfile)
class ShopProfileAdmin(admin.ModelAdmin):

    list_display = (
        "shop_name",
        "owner_name",
        "phone",
        "city",
        "state",
    )

    search_fields = (
        "shop_name",
        "owner_name",
        "phone",
        "gstin",
    )

    list_per_page = 20