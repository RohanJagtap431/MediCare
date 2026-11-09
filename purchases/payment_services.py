
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import Purchase, PurchasePayment


@transaction.atomic
def add_purchase_payment(
    purchase_id,
    amount,
    payment_method,
    received_by=None,
    transaction_reference="",
    notes=""
):
    # Lock purchase to prevent concurrent overpayments
    try:
        purchase = (
            Purchase.objects
            .select_for_update()
            .get(id=purchase_id)
        )
    except Purchase.DoesNotExist:
        raise ValueError("Purchase not found.")

    # Only received purchases can be paid
    if purchase.purchase_status != "RECEIVED":
        raise ValueError("Receive the purchase before recording payment.")

    # Validate amount
    try:
        amount = Decimal(str(amount))
    except Exception:
        raise ValueError("Invalid payment amount.")

    if not amount.is_finite() or amount <= Decimal("0.00"):
        raise ValueError("Payment amount must be greater than zero.")

    # Validate payment method
    valid_methods = {
        choice[0]
        for choice in PurchasePayment.PAYMENT_METHOD_CHOICES
    }

    if payment_method not in valid_methods:
        raise ValueError("Invalid payment method.")

    # Calculate remaining balance
    remaining_balance = (
        purchase.total_amount - purchase.paid_amount
    )

    if amount > remaining_balance:
        raise ValueError(
            f"Payment cannot exceed remaining balance of ₹{remaining_balance}."
        )

    # Create payment record
    payment = PurchasePayment.objects.create(
        purchase=purchase,
        amount=amount,
        payment_method=payment_method,
        transaction_reference=transaction_reference.strip(),
        notes=notes.strip(),
        received_by=received_by,
    )

    # Update paid amount
    purchase.paid_amount += amount

    # Update payment status
    if purchase.paid_amount >= purchase.total_amount:
        purchase.payment_status = "PAID"
    elif purchase.paid_amount > Decimal("0.00"):
        purchase.payment_status = "PARTIAL"
    else:
        purchase.payment_status = "UNPAID"

    purchase.save(
        update_fields=[
            "paid_amount",
            "payment_status",
            "updated_at",
        ]
    )

    return payment
