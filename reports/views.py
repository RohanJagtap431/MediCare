
import csv
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import (
    Sum,
    Count,
    Q,
    F,
    DecimalField,
    ExpressionWrapper,
)
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date

from sales.models import Sale, SalePayment
from purchases.models import Purchase, PurchasePayment
from medicines.models import MedicineBatch


@login_required
def reports_dashboard(request):
    today = timezone.localdate()
    first_day = today.replace(day=1)

    start_date = parse_date(request.GET.get("start_date", "")) or first_day
    end_date = parse_date(request.GET.get("end_date", "")) or today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    sales = Sale.objects.filter(
        sale_date__date__gte=start_date,
        sale_date__date__lte=end_date,
        is_cancelled=False,
    )

    purchases = Purchase.objects.filter(
        purchase_date__gte=start_date,
        purchase_date__lte=end_date,
        purchase_status="RECEIVED",
    )

    sale_payments = SalePayment.objects.filter(
        payment_date__date__gte=start_date,
        payment_date__date__lte=end_date,
    )

    purchase_payments = PurchasePayment.objects.filter(
        payment_date__date__gte=start_date,
        payment_date__date__lte=end_date,
    )

    sales_summary = sales.aggregate(
        total_sales=Sum("total_amount"),
        total_bills=Count("id"),
    )

    purchase_summary = purchases.aggregate(
        total_purchases=Sum("total_amount"),
        total_purchases_count=Count("id"),
    )

    sales_collection = (
        sale_payments.aggregate(total=Sum("amount"))["total"] or 0
    )

    purchase_collection = (
        purchase_payments.aggregate(total=Sum("amount"))["total"] or 0
    )

    context = {
        "start_date": start_date,
        "end_date": end_date,

        "total_sales": sales_summary["total_sales"] or 0,
        "total_bills": sales_summary["total_bills"] or 0,

        "total_purchases": purchase_summary["total_purchases"] or 0,
        "total_purchase_bills": purchase_summary["total_purchases_count"] or 0,

        "sales_collection": sales_collection,
        "purchase_collection": purchase_collection,
    }

    return render(request, "reports/reports_dashboard.html", context)



@login_required
def detailed_sales_report(request):
    today = timezone.localdate()
    first_day = today.replace(day=1)

    start_date = parse_date(request.GET.get("start_date", "")) or first_day
    end_date = parse_date(request.GET.get("end_date", "")) or today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    search_query = request.GET.get("q", "").strip()

    sales = Sale.objects.filter(
        sale_date__date__gte=start_date,
        sale_date__date__lte=end_date,
        is_cancelled=False,
    ).select_related("customer").annotate(
        remaining_balance=F("total_amount") - F("paid_amount")
    )

    if search_query:
        sales = sales.filter(
            Q(invoice_number__icontains=search_query)
            | Q(customer__customer_name__icontains=search_query)
            | Q(customer__phone__icontains=search_query)
        )

    sales = sales.order_by("-sale_date", "-id")

    total_amount = sum(
        (sale.total_amount for sale in sales),
        0
    )

    total_paid = sum(
        (sale.paid_amount for sale in sales),
        0
    )

    total_balance = total_amount - total_paid

    # CSV Export
    if request.GET.get("export") == "csv":
        response = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        response["Content-Disposition"] = (
            'attachment; filename="medicare_sales_report.csv"'
        )

        response.write("\ufeff")
        writer = csv.writer(response)

        writer.writerow([
            "Invoice Number",
            "Sale Date",
            "Customer",
            "Total Amount",
            "Paid Amount",
            "Remaining Balance",
            "Payment Status",
        ])

        for sale in sales:
            writer.writerow([
                sale.invoice_number,
                timezone.localtime(sale.sale_date).strftime("%d-%m-%Y %I:%M %p"),
                sale.customer.customer_name if sale.customer else "Walk-in Customer",
                sale.total_amount,
                sale.paid_amount,
                sale.remaining_balance,
                sale.payment_status,
            ])

        return response

    context = {
        "sales": sales,
        "start_date": start_date,
        "end_date": end_date,
        "search_query": search_query,
        "total_bills": sales.count(),
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_balance": total_balance,
    }

    return render(
        request,
        "reports/detailed_sales_report.html",
        context
    )


@login_required
def detailed_purchase_report(request):
    today = timezone.localdate()
    first_day = today.replace(day=1)

    start_date = parse_date(request.GET.get("start_date", "")) or first_day
    end_date = parse_date(request.GET.get("end_date", "")) or today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    search_query = request.GET.get("q", "").strip()

    purchases = Purchase.objects.filter(
        purchase_date__gte=start_date,
        purchase_date__lte=end_date,
        purchase_status="RECEIVED",
    ).select_related("supplier").annotate(
        remaining_balance=F("total_amount") - F("paid_amount")
    )

    if search_query:
        purchases = purchases.filter(
            Q(invoice_number__icontains=search_query)
            | Q(supplier__supplier_name__icontains=search_query)
            | Q(supplier__phone__icontains=search_query)
        )

    purchases = purchases.order_by("-purchase_date", "-id")

    total_amount = sum(
        (purchase.total_amount for purchase in purchases),
        0
    )

    total_paid = sum(
        (purchase.paid_amount for purchase in purchases),
        0
    )

    total_balance = total_amount - total_paid

    # CSV Export
    if request.GET.get("export") == "csv":
        response = HttpResponse(
            content_type="text/csv; charset=utf-8"
        )
        response["Content-Disposition"] = (
            'attachment; filename="medicare_purchase_report.csv"'
        )

        response.write("\ufeff")
        writer = csv.writer(response)

        writer.writerow([
            "Invoice Number",
            "Purchase Date",
            "Supplier",
            "Total Amount",
            "Paid Amount",
            "Remaining Balance",
            "Payment Status",
        ])

        for purchase in purchases:
            writer.writerow([
                purchase.invoice_number,
                purchase.purchase_date.strftime("%d-%m-%Y"),
                purchase.supplier.supplier_name,
                purchase.total_amount,
                purchase.paid_amount,
                purchase.remaining_balance,
                purchase.payment_status,
            ])

        return response

    context = {
        "purchases": purchases,
        "start_date": start_date,
        "end_date": end_date,
        "search_query": search_query,
        "total_bills": purchases.count(),
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_balance": total_balance,
    }

    return render(
        request,
        "reports/detailed_purchase_report.html",
        context
    )



@login_required
def stock_valuation_report(request):
    today = timezone.localdate()

    search_query = request.GET.get("q", "").strip()

    batches = MedicineBatch.objects.select_related("medicine")

    if search_query:
        batches = batches.filter(
            Q(medicine__name__icontains=search_query)
            | Q(batch_number__icontains=search_query)
        )

    batches = batches.order_by("medicine__name", "expiry_date")

    for batch in batches:
        batch.stock_purchase_value = (
            batch.quantity * batch.purchase_price
        )
        batch.stock_mrp_value = (
            batch.quantity * batch.mrp
        )

        if batch.expiry_date <= today:
            batch.valuation_status = "EXPIRED"
        elif batch.quantity == 0:
            batch.valuation_status = "OUT"
        elif batch.quantity <= batch.minimum_stock_level:
            batch.valuation_status = "LOW"
        else:
            batch.valuation_status = "AVAILABLE"

    saleable_batches = MedicineBatch.objects.filter(
        expiry_date__gt=today,
        quantity__gt=0,
    )

    expired_batches = MedicineBatch.objects.filter(
        expiry_date__lte=today,
        quantity__gt=0,
    )

    saleable_summary = saleable_batches.aggregate(
        total_quantity=Coalesce(Sum("quantity"), 0),
        purchase_value=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                )
            ),
            Decimal("0.00"),
        ),
        mrp_value=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("quantity") * F("mrp"),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                )
            ),
            Decimal("0.00"),
        ),
    )

    expired_summary = expired_batches.aggregate(
        total_quantity=Coalesce(Sum("quantity"), 0),
        purchase_value=Coalesce(
            Sum(
                ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=18, decimal_places=2),
                )
            ),
            Decimal("0.00"),
        ),
    )

    context = {
        "batches": batches,
        "search_query": search_query,

        "total_stock_quantity": saleable_summary["total_quantity"],
        "total_purchase_value": saleable_summary["purchase_value"],
        "total_mrp_value": saleable_summary["mrp_value"],

        "estimated_margin": (
            saleable_summary["mrp_value"]
            - saleable_summary["purchase_value"]
        ),

        "expired_stock_quantity": expired_summary["total_quantity"],
        "expired_stock_value": expired_summary["purchase_value"],
    }

    return render(
        request,
        "reports/stock_valuation_report.html",
        context,
    )
