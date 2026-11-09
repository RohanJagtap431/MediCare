
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Count, Q
from django.shortcuts import render
from django.utils import timezone

from medicines.models import MedicineBatch


@login_required
def stock_list(request):

    today = timezone.localdate()

    search_query = request.GET.get("q", "").strip()
    stock_filter = request.GET.get("status", "").strip()

    batches = MedicineBatch.objects.select_related(
        "medicine",
        "medicine__category",
        "medicine__manufacturer",
    )

    if search_query:
        batches = batches.filter(
            Q(medicine__name__icontains=search_query)
            | Q(batch_number__icontains=search_query)
        )

    if stock_filter == "LOW":
        batches = batches.filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock_level"),
            expiry_date__gt=today,
        )

    elif stock_filter == "OUT":
        batches = batches.filter(quantity=0)

    elif stock_filter == "EXPIRED":
        batches = batches.filter(expiry_date__lte=today)

    elif stock_filter == "AVAILABLE":
        batches = batches.filter(
            quantity__gt=F("minimum_stock_level"),
            expiry_date__gt=today,
        )

    batches = batches.order_by("expiry_date", "medicine__name")

    total_batches = MedicineBatch.objects.count()

    total_stock = (
        MedicineBatch.objects
        .filter(expiry_date__gt=today)
        .aggregate(total=Sum("quantity"))["total"]
        or 0
    )

    low_stock_count = (
        MedicineBatch.objects
        .filter(
            quantity__gt=0,
            quantity__lte=F("minimum_stock_level"),
            expiry_date__gt=today,
        )
        .count()
    )

    out_of_stock_count = (
        MedicineBatch.objects
        .filter(quantity=0, expiry_date__gt=today)
        .count()
    )

    expired_count = MedicineBatch.objects.filter(
        expiry_date__lte=today
    ).count()

    context = {
        "batches": batches,
        "search_query": search_query,
        "selected_status": stock_filter,
        "total_batches": total_batches,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "expired_count": expired_count,
    }

    return render(
        request,
        "inventory/stock_list.html",
        context,
    )




@login_required
def expiry_list(request):
    today = timezone.localdate()
    warning_date = today + timedelta(days=30)
    critical_date = today + timedelta(days=7)

    search_query = request.GET.get("q", "").strip()
    expiry_filter = request.GET.get("status", "").strip()

    batches = MedicineBatch.objects.select_related("medicine")

    if search_query:
        batches = batches.filter(
            Q(medicine__name__icontains=search_query)
            | Q(batch_number__icontains=search_query)
        )

    if expiry_filter == "EXPIRED":
        batches = batches.filter(expiry_date__lte=today)

    elif expiry_filter == "CRITICAL":
        batches = batches.filter(
            expiry_date__gt=today,
            expiry_date__lte=critical_date
        )

    elif expiry_filter == "UPCOMING":
        batches = batches.filter(
            expiry_date__gt=critical_date,
            expiry_date__lte=warning_date
        )

    elif expiry_filter == "SAFE":
        batches = batches.filter(expiry_date__gt=warning_date)

    batches = batches.order_by("expiry_date", "medicine__name")

    for batch in batches:
        if batch.expiry_date <= today:
            batch.expiry_status = "EXPIRED"
        elif batch.expiry_date <= critical_date:
            batch.expiry_status = "CRITICAL"
        elif batch.expiry_date <= warning_date:
            batch.expiry_status = "UPCOMING"
        else:
            batch.expiry_status = "SAFE"

    expired_stock_alerts = (
        MedicineBatch.objects
        .filter(expiry_date__lte=today, quantity__gt=0)
        .select_related("medicine")
        .order_by("expiry_date")[:5]
    )

    near_expiry_alerts = (
        MedicineBatch.objects
        .filter(
            expiry_date__gt=today,
            expiry_date__lte=warning_date,
            quantity__gt=0
        )
        .select_related("medicine")
        .order_by("expiry_date")[:5]
    )

    context = {
        "batches": batches,
        "today": today,
        "search_query": search_query,
        "expiry_filter": expiry_filter,

        "expired_count": MedicineBatch.objects.filter(
            expiry_date__lte=today
        ).count(),

        "critical_count": MedicineBatch.objects.filter(
            expiry_date__gt=today,
            expiry_date__lte=critical_date
        ).count(),

        "upcoming_count": MedicineBatch.objects.filter(
            expiry_date__gt=critical_date,
            expiry_date__lte=warning_date
        ).count(),

        "safe_count": MedicineBatch.objects.filter(
            expiry_date__gt=warning_date
        ).count(),

        "expired_stock_alerts": expired_stock_alerts,
        "near_expiry_alerts": near_expiry_alerts,
    }

    return render(request, "inventory/expiry_list.html", context)



