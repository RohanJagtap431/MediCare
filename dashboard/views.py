
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import render
from django.utils import timezone

from sales.models import Sale
from purchases.models import Purchase
from medicines.models import MedicineBatch
from expenses.models import Expense


@login_required
def dashboard(request):

    today = timezone.localdate()

    is_admin = (
        request.user.is_superuser
        or getattr(request.user, "role", None) == "ADMIN"
    )

    # ---------------------------------
    # SALES
    # ---------------------------------

    sales_queryset = Sale.objects.filter(
        is_cancelled=False
    )

    # Staff sees their own sales
    if not is_admin:
        sales_queryset = sales_queryset.filter(
            created_by=request.user
        )

    today_sales = sales_queryset.filter(
        sale_date__date=today
    )

    today_sales_amount = (
        today_sales.aggregate(total=Sum("total_amount"))["total"]
        or Decimal("0.00")
    )

    today_bills_count = today_sales.count()

    recent_bills = (
        sales_queryset
        .select_related("customer")
        .order_by("-sale_date", "-id")[:5]
    )

    # ---------------------------------
    # STOCK
    # ---------------------------------

    low_stock_batches = MedicineBatch.objects.filter(
        expiry_date__gt=today,
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level")
    ).select_related("medicine").order_by("quantity")[:5]

    low_stock_count = MedicineBatch.objects.filter(
        expiry_date__gt=today,
        quantity__gt=0,
        quantity__lte=F("minimum_stock_level")
    ).count()

    # ---------------------------------
    # EXPIRY
    # ---------------------------------

    next_30_days = today + timedelta(days=30)

    expired_count = MedicineBatch.objects.filter(
        expiry_date__lte=today,
        quantity__gt=0
    ).count()

    expiring_batches = MedicineBatch.objects.filter(
        expiry_date__gt=today,
        expiry_date__lte=next_30_days,
        quantity__gt=0
    ).select_related("medicine").order_by("expiry_date")[:5]

    expiring_count = MedicineBatch.objects.filter(
        expiry_date__gt=today,
        expiry_date__lte=next_30_days,
        quantity__gt=0
    ).count()

    # ---------------------------------
    # COMMON CONTEXT
    # ---------------------------------

    context = {
        "is_admin": is_admin,
        "today": today,

        "today_sales_amount": today_sales_amount,
        "today_bills_count": today_bills_count,

        "low_stock_count": low_stock_count,
        "low_stock_batches": low_stock_batches,

        "expired_count": expired_count,
        "expiring_count": expiring_count,
        "expiring_batches": expiring_batches,

        "recent_bills": recent_bills,
    }

    # ---------------------------------
    # ADMIN ONLY DATA
    # ---------------------------------

    if is_admin:

        today_purchases = Purchase.objects.filter(
            purchase_date=today,
            purchase_status="RECEIVED"
        )

        today_purchases_amount = (
            today_purchases.aggregate(total=Sum("total_amount"))["total"]
            or Decimal("0.00")
        )

        today_expenses = Expense.objects.filter(
            expense_date=today
        )

        today_expenses_amount = (
            today_expenses.aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        context.update({
            "today_purchases_amount": today_purchases_amount,
            "today_purchases_count": today_purchases.count(),

            "today_expenses_amount": today_expenses_amount,
            "today_expenses_count": today_expenses.count(),
        })

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )
