from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Purchase


@transaction.atomic
def receive_purchase(purchase_id):

    purchase = (
        Purchase.objects
        .select_for_update()
        .get(id=purchase_id)
    )

    # Prevent duplicate stock entry
    if purchase.purchase_status == "RECEIVED":
        raise ValueError("This purchase has already been received.")

    # Get purchase items
    items = purchase.items.select_related("batch")

    if not items.exists():
        raise ValueError("Cannot receive purchase without items.")

    # Add stock batch-wise
    for item in items:

        stock_quantity = item.quantity + item.free_quantity

        item.batch.__class__.objects.filter(
            id=item.batch_id
        ).update(
            quantity=F("quantity") + stock_quantity
        )

    # Update purchase status
    purchase.purchase_status = "RECEIVED"
    purchase.received_at = timezone.now()

    purchase.save(
        update_fields=[
            "purchase_status",
            "received_at",
            "updated_at",
        ]
    )

    return purchase