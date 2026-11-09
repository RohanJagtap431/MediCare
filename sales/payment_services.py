
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Sum

from .models import Sale, SalePayment


@transaction.atomic
def add_sale_payment(
    sale_id,
    amount,
    payment_method,
    transaction_reference="",
    notes="",
    received_by=None,
):
    sale = (
        Sale.objects
        .select_for_update()
        .get(id=sale_id)
    )

    # Prevent payment on cancelled bills
    if sale.is_cancelled:
        raise ValueError(
            "Cannot accept payment for a cancelled bill."
        )

    # Validate payment amount
    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Enter a valid payment amount.")

    if not amount.is_finite() or amount <= Decimal("0.00"):
        raise ValueError(
            "Payment amount must be greater than zero."
        )

    # Ensure sale has items
    if not sale.items.exists():
        raise ValueError("Sale has no items.")

    # Ensure stock has been deducted
    if sale.items.filter(stock_deducted=False).exists():
        raise ValueError(
            "Process the sale before accepting payment."
        )

    # Validate payment method
    if payment_method not in dict(SalePayment.PAYMENT_METHOD_CHOICES):
        raise ValueError("Invalid payment method.")

    # Calculate total payments received
    total_paid = (
        SalePayment.objects
        .filter(sale=sale)
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    # Calculate outstanding balance
    remaining = sale.total_amount - total_paid

    if remaining <= Decimal("0.00"):
        raise ValueError("This bill is already fully paid.")

    if amount > remaining:
        raise ValueError(
            f"Payment exceeds outstanding balance of {remaining}."
        )

    # Create payment record
    payment = SalePayment.objects.create(
        sale=sale,
        amount=amount,
        payment_method=payment_method,
        transaction_reference=transaction_reference,
        notes=notes,
        received_by=received_by,
    )

    # Update sale payment details
    new_total_paid = total_paid + amount

    sale.paid_amount = new_total_paid

    if new_total_paid >= sale.total_amount:
        sale.payment_status = "PAID"
    else:
        sale.payment_status = "PARTIAL"

    sale.payment_method = payment_method

    sale.save(
        update_fields=[
            "paid_amount",
            "payment_status",
            "payment_method",
        ]
    )

    return payment
