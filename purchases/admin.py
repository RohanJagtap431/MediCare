from django.contrib import admin, messages
from .models import Purchase, PurchaseItem
from .services import receive_purchase


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    autocomplete_fields = ["batch"]

    def has_add_permission(self, request, obj=None):
        if obj and obj.purchase_status == "RECEIVED":
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.purchase_status == "RECEIVED":
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.purchase_status == "RECEIVED":
            return [
                field.name
                for field in self.model._meta.fields
            ]
        return []

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "supplier",
        "purchase_date",
        "total_amount",
        "paid_amount",
        "payment_status",
        "purchase_status",
        "received_at",
    )

    search_fields = (
        "invoice_number",
        "supplier__supplier_name",
    )

    list_filter = (
        "purchase_status",
        "payment_status",
        "payment_method",
        "purchase_date",
    )

    inlines = [PurchaseItemInline]

    readonly_fields = (
        "created_at",
        "updated_at",
        "received_at",
    )

    list_per_page = 25

    actions = ["receive_selected_purchases"]

    @admin.action(description="Receive selected purchases and update stock")
    def receive_selected_purchases(self, request, queryset):

        success_count = 0
        error_count = 0

        for purchase in queryset:

            try:
                receive_purchase(purchase.id)
                success_count += 1

            except ValueError as error:
                error_count += 1
                self.message_user(
                    request,
                    f"{purchase.invoice_number}: {error}",
                    level=messages.ERROR,
                )

            except Exception:
                error_count += 1
                self.message_user(
                    request,
                    f"{purchase.invoice_number}: Unexpected error. No stock was changed for this purchase.",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} purchase(s) received successfully.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} purchase(s) could not be received.",
                level=messages.WARNING,
            )
            
            
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj and obj.purchase_status == "RECEIVED":
            readonly.extend([
                "invoice_number",
                "supplier",
                "purchase_date",
                "subtotal",
                "discount_amount",
                "gst_amount",
                "total_amount",
                "paid_amount",
                "payment_status",
                "payment_method",
                "notes",
                "created_by",
                "purchase_status",
            ])

        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and obj.purchase_status == "RECEIVED":
            return False
        return super().has_delete_permission(request, obj)


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):

    list_display = (
        "purchase",
        "batch",
        "quantity",
        "free_quantity",
        "purchase_price",
        "total_amount",
    )

    search_fields = (
        "purchase__invoice_number",
        "batch__medicine__name",
        "batch__batch_number",
    )

    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj and obj.purchase.purchase_status == "RECEIVED":
            readonly.extend([
                "purchase",
                "batch",
                "quantity",
                "free_quantity",
                "purchase_price",
                "mrp",
                "discount_amount",
                "gst_percentage",
                "total_amount",
            ])

        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and obj.purchase.purchase_status == "RECEIVED":
            return False

        return super().has_delete_permission(request, obj)