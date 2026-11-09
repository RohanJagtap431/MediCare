
from collections import defaultdict
from decimal import Decimal
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from core.models import ShopProfile

from .forms import SaleForm, SaleItemFormSet
from .models import Sale
from .payment_forms import SalePaymentForm
from .payment_services import add_sale_payment
from .services import process_sale, cancel_sale, delete_sale


@login_required
def sale_invoice(request, sale_id):

    sale = get_object_or_404(
        Sale.objects.select_related("customer", "created_by"),
        id=sale_id,
    )

    items = sale.items.select_related(
        "batch",
        "batch__medicine",
    )

    payments = sale.payments.all()

    shop = ShopProfile.objects.first()

    context = {
        "sale": sale,
        "items": items,
        "payments": payments,
        "shop": shop,
        "remaining_balance": (
            sale.total_amount - sale.paid_amount
        ),
    }

    return render(
        request,
        "sales/invoice.html",
        context,
    )


@login_required
def sale_create(request):

    if request.method == "POST":
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            batch_quantities = defaultdict(int)
            has_manual_errors = False

            for item_form in formset:

                if not item_form.cleaned_data:
                    continue

                if item_form.cleaned_data.get("DELETE"):
                    continue

                batch = item_form.cleaned_data["batch"]
                quantity = item_form.cleaned_data["quantity"]
                price = item_form.cleaned_data["selling_price"]

                discount = (
                    item_form.cleaned_data.get("discount_amount")
                    or Decimal("0")
                )

                gst_percentage = (
                    item_form.cleaned_data.get("gst_percentage")
                    or Decimal("0")
                )

                if quantity <= 0:
                    item_form.add_error(
                        "quantity",
                        "Quantity must be greater than zero.",
                    )
                    has_manual_errors = True

                if price <= 0:
                    item_form.add_error(
                        "selling_price",
                        "Selling price must be greater than zero.",
                    )
                    has_manual_errors = True

                if discount < 0 or discount > quantity * price:
                    item_form.add_error(
                        "discount_amount",
                        "Invalid discount amount.",
                    )
                    has_manual_errors = True

                if gst_percentage < 0:
                    item_form.add_error(
                        "gst_percentage",
                        "GST cannot be negative.",
                    )
                    has_manual_errors = True

                batch_quantities[batch.id] += quantity

            for item_form in formset:

                if not item_form.cleaned_data:
                    continue

                if item_form.cleaned_data.get("DELETE"):
                    continue

                batch = item_form.cleaned_data["batch"]

                if batch_quantities[batch.id] > batch.quantity:
                    item_form.add_error(
                        "quantity",
                        f"Only {batch.quantity} units available.",
                    )
                    has_manual_errors = True

            if has_manual_errors:
                return render(
                    request,
                    "sales/sale_form.html",
                    {
                        "form": form,
                        "formset": formset,
                    },
                )

            try:
                with transaction.atomic():

                    sale = form.save(commit=False)

                    sale.invoice_number = (
                        f"INV-{timezone.localdate():%Y%m%d}-"
                        f"{uuid4().hex[:8].upper()}"
                    )

                    sale.created_by = request.user
                    sale.paid_amount = Decimal("0")
                    sale.payment_status = "UNPAID"
                    sale.payment_method = ""
                    sale.subtotal = Decimal("0")
                    sale.gst_amount = Decimal("0")
                    sale.total_amount = Decimal("0")

                    sale.save()

                    items = [
                        item_form.save(commit=False)
                        for item_form in formset
                        if item_form.cleaned_data
                        and not item_form.cleaned_data.get("DELETE")
                    ]

                    subtotal = Decimal("0")
                    item_discount_total = Decimal("0")
                    gst_total = Decimal("0")

                    for item in items:

                        quantity = item.quantity
                        price = item.selling_price

                        discount = (
                            item.discount_amount or Decimal("0")
                        )

                        gst_percentage = (
                            item.gst_percentage or Decimal("0")
                        )

                        base_amount = quantity * price
                        taxable_amount = base_amount - discount

                        gst_amount = (
                            taxable_amount * gst_percentage
                        ) / Decimal("100")

                        item_total = taxable_amount + gst_amount

                        item.sale = sale
                        item.gst_amount = gst_amount
                        item.total_amount = item_total
                        item.stock_deducted = False

                        item.save()

                        subtotal += base_amount
                        item_discount_total += discount
                        gst_total += gst_amount

                    header_discount = (
                        sale.discount_amount or Decimal("0")
                    )

                    if header_discount < 0:
                        raise ValueError(
                            "Bill discount cannot be negative."
                        )

                    total_discount = (
                        item_discount_total + header_discount
                    )

                    if total_discount > subtotal:
                        raise ValueError(
                            "Total discount cannot exceed subtotal."
                        )

                    sale.subtotal = subtotal
                    sale.discount_amount = total_discount
                    sale.gst_amount = gst_total

                    sale.total_amount = (
                        subtotal - total_discount + gst_total
                    )

                    sale.save(
                        update_fields=[
                            "subtotal",
                            "discount_amount",
                            "gst_amount",
                            "total_amount",
                        ]
                    )

                    # Deduct stock after bill creation
                    process_sale(sale.id)

                messages.success(
                    request,
                    "Bill created successfully.",
                )

                return redirect(
                    "sales:sale_invoice",
                    sale_id=sale.id,
                )

            except ValueError as error:
                messages.error(request, str(error))

    else:
        form = SaleForm()
        formset = SaleItemFormSet()

    return render(
        request,
        "sales/sale_form.html",
        {
            "form": form,
            "formset": formset,
        },
    )


@login_required
def bill_list(request):

    search_query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    bills = Sale.objects.select_related(
        "customer",
        "created_by",
    ).all()

    if search_query:
        bills = bills.filter(
            Q(invoice_number__icontains=search_query)
            | Q(customer__customer_name__icontains=search_query)
        )

    valid_statuses = ["PAID", "PARTIAL", "UNPAID"]

    if status in valid_statuses:
        bills = bills.filter(payment_status=status)

    paginator = Paginator(bills, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for bill in page_obj.object_list:
        bill.remaining_balance = (
            bill.total_amount - bill.paid_amount
        )

    context = {
        "page_obj": page_obj,
        "bills": page_obj.object_list,
        "search_query": search_query,
        "selected_status": status,
        "total_bills": bills.count(),
    }

    return render(
        request,
        "sales/bill_list.html",
        context,
    )


@login_required
def sale_add_payment(request, sale_id):

    sale = get_object_or_404(Sale, id=sale_id)

    remaining_balance = sale.total_amount - sale.paid_amount

    if sale.is_cancelled:
        messages.error(
            request,
            "Cannot accept payment for a cancelled bill.",
        )
        return redirect(
            "sales:sale_invoice",
            sale_id=sale.id,
        )

    if remaining_balance <= Decimal("0.00"):
        messages.info(
            request,
            "This bill is already fully paid.",
        )
        return redirect(
            "sales:sale_invoice",
            sale_id=sale.id,
        )

    if request.method == "POST":

        form = SalePaymentForm(request.POST)

        if form.is_valid():

            try:
                payment = add_sale_payment(
                    sale_id=sale.id,
                    amount=form.cleaned_data["amount"],
                    payment_method=form.cleaned_data["payment_method"],
                    transaction_reference=form.cleaned_data[
                        "transaction_reference"
                    ],
                    notes=form.cleaned_data["notes"],
                    received_by=request.user,
                )

                messages.success(
                    request,
                    f"Payment of ₹{payment.amount} received successfully.",
                )

                return redirect(
                    "sales:sale_invoice",
                    sale_id=sale.id,
                )

            except ValueError as error:
                messages.error(request, str(error))

    else:
        form = SalePaymentForm()

    context = {
        "sale": sale,
        "form": form,
        "remaining_balance": remaining_balance,
    }

    return render(
        request,
        "sales/payment_form.html",
        context,
    )


@admin_required
@require_POST
def sale_cancel(request, sale_id):

    reason = request.POST.get("reason", "").strip()

    try:
        sale = cancel_sale(sale_id, reason)

        messages.success(
            request,
            f"Bill {sale.invoice_number} cancelled successfully. Stock restored.",
        )

    except (ValueError, Sale.DoesNotExist) as error:
        messages.error(request, str(error))

    return redirect("sales:bill_list")


@admin_required
@require_POST
def sale_delete(request, sale_id):

    try:
        invoice_number = delete_sale(sale_id)

        messages.success(
            request,
            f"Bill {invoice_number} permanently deleted.",
        )

    except (ValueError, Sale.DoesNotExist) as error:
        messages.error(request, str(error))

    return redirect("sales:bill_list")
