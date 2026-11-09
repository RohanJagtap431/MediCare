
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Sale


@transaction.atomic
def process_sale(sale_id):

    sale = (
        Sale.objects
        .select_for_update()
        .get(id=sale_id)
    )

    if sale.is_cancelled:
        raise ValueError("Cannot process a cancelled bill.")

    items = list(
        sale.items.select_related("batch", "batch__medicine")
    )

    if not items:
        raise ValueError("Cannot process sale without items.")

    if any(item.stock_deducted for item in items):
        raise ValueError(
            "Stock has already been deducted or sale is partially processed."
        )

    today = timezone.localdate()

    for item in items:

        batch = item.batch

        if batch.expiry_date <= today:
            raise ValueError(
                f"{batch.medicine.name} batch {batch.batch_number} is expired."
            )

        if item.quantity <= 0:
            raise ValueError("Sale quantity must be greater than zero.")

        updated = batch.__class__.objects.filter(
            id=batch.id,
            expiry_date__gt=today,
            quantity__gte=item.quantity,
        ).update(
            quantity=F("quantity") - item.quantity
        )

        if updated == 0:
            raise ValueError(
                f"Insufficient stock or expired batch: "
                f"{batch.medicine.name} - {batch.batch_number}"
            )

        item.stock_deducted = True
        item.save(update_fields=["stock_deducted"])

    return sale


@transaction.atomic
def cancel_sale(sale_id, reason):

    sale = (
        Sale.objects
        .select_for_update()
        .get(id=sale_id)
    )

    if sale.is_cancelled:
        raise ValueError("This bill is already cancelled.")

    if sale.payments.exists() or sale.paid_amount > 0:
        raise ValueError(
            "Cannot cancel a bill with payment records. "
            "Handle refund/payment reversal first."
        )

    if not reason or not reason.strip():
        raise ValueError("Cancellation reason is required.")

    items = list(
        sale.items.select_related("batch")
    )

    if not items:
        raise ValueError("Cannot cancel a bill without items.")

    for item in items:

        if item.stock_deducted:

            item.batch.__class__.objects.filter(
                id=item.batch_id
            ).update(
                quantity=F("quantity") + item.quantity
            )

            item.stock_deducted = False
            item.save(update_fields=["stock_deducted"])

    sale.is_cancelled = True
    sale.cancelled_at = timezone.now()
    sale.cancellation_reason = reason.strip()

    sale.save(
        update_fields=[
            "is_cancelled",
            "cancelled_at",
            "cancellation_reason",
        ]
    )

    return sale


@transaction.atomic
def delete_sale(sale_id):

    sale = (
        Sale.objects
        .select_for_update()
        .get(id=sale_id)
    )

    if sale.payments.exists() or sale.paid_amount > 0:
        raise ValueError(
            "Cannot permanently delete a bill with payment records."
        )

    items = list(
        sale.items.select_related("batch")
    )

    # Restore stock if the bill was processed but not cancelled.
    for item in items:

        if item.stock_deducted:

            item.batch.__class__.objects.filter(
                id=item.batch_id
            ).update(
                quantity=F("quantity") + item.quantity
            )

            item.stock_deducted = False
            item.save(update_fields=["stock_deducted"])

    invoice_number = sale.invoice_number

    sale.delete()

    return invoice_number
