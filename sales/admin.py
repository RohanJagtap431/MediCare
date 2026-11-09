from django.contrib import admin, messages

from .models import Sale, SaleItem, SalePayment
from .services import process_sale


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    autocomplete_fields = ["batch"]
    
    def has_add_permission(self, request, obj=None):
        if obj and obj.items.filter(stock_deducted=True).exists():
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.items.filter(stock_deducted=True).exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.items.filter(stock_deducted=True).exists():
            return [
                field.name
                for field in self.model._meta.fields
            ]
        return []


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "customer",
        "sale_date",
        "total_amount",
        "paid_amount",
        "payment_status",
    )

    search_fields = (
        "invoice_number",
        "customer__customer_name",
        "customer__phone",
    )

    list_filter = (
        "payment_status",
        "payment_method",
        "sale_date",
    )

    inlines = [SaleItemInline]

    readonly_fields = (
        "sale_date",
        "created_at",
    )

    list_per_page = 25

    actions = ["process_selected_sales"]

    @admin.action(description="Process selected sales and deduct stock")
    def process_selected_sales(self, request, queryset):

        success_count = 0
        error_count = 0

        for sale in queryset:

            try:
                process_sale(sale.id)
                success_count += 1

            except ValueError as error:
                error_count += 1

                self.message_user(
                    request,
                    f"{sale.invoice_number}: {error}",
                    level=messages.ERROR,
                )

            except Exception:
                error_count += 1

                self.message_user(
                    request,
                    f"{sale.invoice_number}: Unexpected error.",
                    level=messages.ERROR,
                )

        if success_count:
            self.message_user(
                request,
                f"{success_count} sale(s) processed successfully.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"{error_count} sale(s) could not be processed.",
                level=messages.WARNING,
            )
            
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj and obj.items.filter(stock_deducted=True).exists():
            readonly.extend([
                "invoice_number",
                "customer",
                "subtotal",
                "discount_amount",
                "gst_amount",
                "total_amount",
                "paid_amount",
                "payment_status",
                "payment_method",
                "notes",
                "created_by",
            ])

        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and obj.items.filter(stock_deducted=True).exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):

    list_display = (
        "sale",
        "batch",
        "quantity",
        "selling_price",
        "discount_amount",
        "gst_percentage",
        "total_amount",
        "stock_deducted",
    )

    search_fields = (
        "sale__invoice_number",
        "batch__medicine__name",
        "batch__batch_number",
    )

    list_filter = ("stock_deducted",)

    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))

        if obj and obj.stock_deducted:
            readonly.extend([
                "sale",
                "batch",
                "quantity",
                "selling_price",
                "discount_amount",
                "gst_percentage",
                "gst_amount",
                "total_amount",
            ])

        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and obj.stock_deducted:
            return False

        return super().has_delete_permission(request, obj)
    
    
@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):

    list_display = (
        "sale",
        "amount",
        "payment_method",
        "transaction_reference",
        "received_by",
        "payment_date",
    )

    search_fields = (
        "sale__invoice_number",
        "transaction_reference",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )

    readonly_fields = (
        "sale",
        "amount",
        "payment_method",
        "transaction_reference",
        "notes",
        "received_by",
        "payment_date",
    )

    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False