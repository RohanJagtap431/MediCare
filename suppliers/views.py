
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from accounts.decorators import admin_required

from .models import Supplier
from .forms import SupplierForm


# =====================================
# SUPPLIER LIST
# ADMIN + STAFF
# =====================================

@login_required
def supplier_list(request):

    search = request.GET.get("search", "").strip()

    suppliers = Supplier.objects.all().order_by("supplier_name")

    if search:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search) |
            Q(gstin__icontains=search)
        )

    paginator = Paginator(suppliers, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "suppliers": page_obj,
        "page_obj": page_obj,
        "search": search,
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "suppliers/supplier_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "suppliers/supplier_list.html",
        context
    )


# =====================================
# SUPPLIER DELETE
# ADMIN ONLY
# =====================================

@admin_required
def supplier_delete(request, pk):

    if request.method == "POST":

        supplier = get_object_or_404(Supplier, pk=pk)

        try:
            supplier_name = supplier.supplier_name
            supplier.delete()

            messages.success(
                request,
                f"{supplier_name} deleted successfully."
            )

        except ProtectedError:
            messages.error(
                request,
                "This supplier cannot be deleted because purchase records are linked to it."
            )

    return redirect("suppliers:supplier_list")


# =====================================
# SUPPLIER ACTIVATE / DEACTIVATE
# ADMIN ONLY
# =====================================

@admin_required
def supplier_toggle_status(request, pk):

    if request.method == "POST":

        supplier = get_object_or_404(Supplier, pk=pk)

        supplier.is_active = not supplier.is_active
        supplier.save(update_fields=["is_active", "updated_at"])

        status = "activated" if supplier.is_active else "deactivated"

        messages.success(
            request,
            f"{supplier.supplier_name} {status} successfully."
        )

    return redirect("suppliers:supplier_list")


# =====================================
# SUPPLIER UPDATE
# ADMIN ONLY
# =====================================

@admin_required
def supplier_update(request, pk):

    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            supplier = form.save()

            messages.success(
                request,
                f"{supplier.supplier_name} updated successfully."
            )

            return redirect("suppliers:supplier_list")

    else:
        form = SupplierForm(instance=supplier)

    context = {
        "form": form,
        "page_title": "Edit Supplier",
        "button_text": "Update Supplier",
        "supplier": supplier,
    }

    return render(
        request,
        "suppliers/supplier_form.html",
        context
    )


# =====================================
# SUPPLIER CREATE
# ADMIN ONLY
# =====================================

@admin_required
def supplier_create(request):

    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save()

            messages.success(
                request,
                f"{supplier.supplier_name} added successfully."
            )

            return redirect("suppliers:supplier_list")

    else:
        form = SupplierForm()

    context = {
        "form": form,
        "page_title": "Add Supplier",
        "button_text": "Save Supplier",
    }

    return render(
        request,
        "suppliers/supplier_form.html",
        context
    )
