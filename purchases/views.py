
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required

from .models import Purchase, PurchasePayment
from .forms import PurchaseForm, PurchaseItemFormSet
from .services import receive_purchase
from .payment_forms import PurchasePaymentForm
from .payment_services import add_purchase_payment


# =====================================
# CREATE PURCHASE
# ADMIN ONLY
# =====================================

@admin_required
def purchase_create(request):

    if request.method == "POST":

        form = PurchaseForm(request.POST)

        if form.is_valid():

            purchase = form.save(commit=False)
            purchase.created_by = request.user
            purchase.purchase_status = "DRAFT"
            purchase.paid_amount = Decimal("0.00")
            purchase.payment_status = "UNPAID"
            purchase.payment_method = ""

            formset = PurchaseItemFormSet(
                request.POST,
                instance=purchase
            )

            if formset.is_valid():

                with transaction.atomic():

                    purchase.save()
                    form.save_m2m()

                    items = formset.save(commit=False)

                    subtotal = Decimal("0.00")
                    item_discount_total = Decimal("0.00")
                    gst_total = Decimal("0.00")

                    for deleted_item in formset.deleted_objects:
                        deleted_item.delete()

                    for item in items:

                        base_amount = (
                            Decimal(item.quantity) *
                            item.purchase_price
                        )

                        item_discount = item.discount_amount

                        taxable_amount = base_amount - item_discount

                        gst_amount = (
                            taxable_amount *
                            item.gst_percentage /
                            Decimal("100")
                        )

                        item.total_amount = taxable_amount + gst_amount

                        item.purchase = purchase
                        item.save()

                        subtotal += base_amount
                        item_discount_total += item_discount
                        gst_total += gst_amount

                    purchase.subtotal = subtotal
                    purchase.discount_amount = (
                        item_discount_total +
                        (purchase.discount_amount or Decimal("0.00"))
                    )
                    purchase.gst_amount = gst_total

                    purchase.total_amount = (
                        subtotal
                        - purchase.discount_amount
                        + gst_total
                    )

                    purchase.save()

                messages.success(
                    request,
                    f"Purchase {purchase.invoice_number} saved as Draft."
                )

                return redirect("purchases:purchase_list")

            else:
                messages.error(
                    request,
                    "Please correct the errors in purchase items."
                )

        else:
            formset = PurchaseItemFormSet(request.POST)

    else:

        form = PurchaseForm(
            initial={"purchase_date": timezone.localdate()}
        )

        formset = PurchaseItemFormSet()

    context = {
        "form": form,
        "formset": formset,
        "page_title": "Create Purchase",
        "button_text": "Save Purchase",
    }

    return render(
        request,
        "purchases/purchase_form.html",
        context
    )


# =====================================
# PURCHASE LIST
# ADMIN + STAFF
# =====================================

@login_required
def purchase_list(request):

    search_query = request.GET.get("q", "").strip()

    purchases = Purchase.objects.select_related(
        "supplier",
        "created_by"
    ).order_by("-purchase_date", "-id")

    if search_query:
        purchases = purchases.filter(
            Q(invoice_number__icontains=search_query) |
            Q(supplier__supplier_name__icontains=search_query)
        )

    paginator = Paginator(purchases, 10)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "purchases": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
    }

    return render(
        request,
        "purchases/purchase_list.html",
        context
    )


# =====================================
# PURCHASE DETAIL
# ADMIN + STAFF
# =====================================

@login_required
def purchase_detail(request, pk):

    purchase = get_object_or_404(
        Purchase.objects.select_related(
            "supplier",
            "created_by"
        ).prefetch_related(
            "items__batch__medicine",
            "payments__received_by"
        ),
        pk=pk
    )

    items = purchase.items.select_related(
        "batch",
        "batch__medicine"
    )

    payment_methods = list(
        purchase.payments.values_list(
            "payment_method",
            flat=True
        ).distinct()
    )

    if not payment_methods:
        display_payment_method = "—"

    elif len(payment_methods) == 1:
        display_payment_method = dict(
            PurchasePayment.PAYMENT_METHOD_CHOICES
        ).get(payment_methods[0], "—")

    else:
        display_payment_method = "Multiple"

    context = {
        "purchase": purchase,
        "items": items,
        "remaining_balance": (
            purchase.total_amount - purchase.paid_amount
        ),
        "display_payment_method": display_payment_method,
    }

    return render(
        request,
        "purchases/purchase_detail.html",
        context
    )


# =====================================
# PURCHASE RECEIVE
# ADMIN ONLY
# =====================================

@admin_required
@require_POST
def purchase_receive(request, pk):

    try:
        purchase = receive_purchase(pk)

        messages.success(
            request,
            f"Purchase {purchase.invoice_number} received successfully. Stock updated."
        )

    except Purchase.DoesNotExist:
        messages.error(request, "Purchase not found.")

    except ValueError as e:
        messages.warning(request, str(e))

    except Exception:
        messages.error(
            request,
            "Something went wrong while receiving purchase."
        )

    return redirect("purchases:purchase_detail", pk=pk)


# =====================================
# PURCHASE ADD PAYMENT
# ADMIN ONLY
# =====================================

@admin_required
def purchase_add_payment(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk
    )

    if purchase.purchase_status != "RECEIVED":
        messages.error(
            request,
            "Receive the purchase before recording payment."
        )
        return redirect(
            "purchases:purchase_detail",
            pk=pk
        )

    remaining_balance = (
        purchase.total_amount - purchase.paid_amount
    )

    if remaining_balance <= 0:
        messages.info(
            request,
            "This purchase is already fully paid."
        )
        return redirect(
            "purchases:purchase_detail",
            pk=pk
        )

    if request.method == "POST":

        form = PurchasePaymentForm(request.POST)

        if form.is_valid():

            try:
                payment = add_purchase_payment(
                    purchase_id=purchase.pk,
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
                    f"Payment of ₹{payment.amount} recorded successfully."
                )

                return redirect(
                    "purchases:purchase_detail",
                    pk=pk
                )

            except ValueError as e:
                form.add_error("amount", str(e))

        messages.error(
            request,
            "Please correct the errors below."
        )

    else:
        form = PurchasePaymentForm()

    context = {
        "purchase": purchase,
        "form": form,
        "remaining_balance": remaining_balance,
    }

    return render(
        request,
        "purchases/payment_form.html",
        context
    )
