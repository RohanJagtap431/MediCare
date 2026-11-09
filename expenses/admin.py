
from django.contrib import admin
from .models import ExpenseCategory, Expense


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "amount",
        "expense_date",
        "payment_method",
        "created_by",
    )
    list_filter = ("category", "payment_method", "expense_date")
    search_fields = (
        "title",
        "reference_number",
        "category__name",
    )
    date_hierarchy = "expense_date"
    readonly_fields = ("created_at", "updated_at")
