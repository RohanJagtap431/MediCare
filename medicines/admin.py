from django.contrib import admin
from .models import MedicineCategory, Manufacturer, Medicine, MedicineBatch

@admin.register(MedicineCategory)
class MedicineCategoryAdmin(admin.ModelAdmin):

    list_display = ("name", "is_active", "created_at")
    search_fields = ("name", "description")
    list_filter = ("is_active",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
    )

    search_fields = ("name", "contact_person", "phone")
    list_filter = ("is_active",)


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "generic_name",
        "category",
        "manufacturer",
        "strength",
        "dosage_form",
        "requires_prescription",
        "is_active",
    )

    search_fields = (
        "name",
        "generic_name",
        "barcode",
    )

    list_filter = (
        "category",
        "dosage_form",
        "requires_prescription",
        "is_active",
    )

    list_per_page = 25
    
@admin.register(MedicineBatch)
class MedicineBatchAdmin(admin.ModelAdmin):

    list_display = (
        "medicine",
        "batch_number",
        "manufacturing_date",
        "expiry_date",
        "purchase_price",
        "mrp",
        "selling_price",
        "quantity",
    )

    search_fields = (
        "medicine__name",
        "batch_number",
    )

    list_filter = (
        "expiry_date",
        "created_at",
    )

    list_per_page = 25
    date_hierarchy = "expiry_date"