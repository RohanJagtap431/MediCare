
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q
from django.db.models.deletion import ProtectedError

from accounts.decorators import admin_required

from .models import Customer
from .forms import CustomerForm


# =====================================
# CUSTOMER LIST
# ADMIN + STAFF
# =====================================

@login_required
def customer_list(request):

    search = request.GET.get("search", "").strip()

    customers = Customer.objects.all().order_by("customer_name")

    if search:
        customers = customers.filter(
            Q(customer_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(alternate_phone__icontains=search) |
            Q(email__icontains=search) |
            Q(city__icontains=search)
        )

    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "customers": page_obj,
        "page_obj": page_obj,
        "search": search,
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "customers/customer_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "customers/customer_list.html",
        context
    )


# =====================================
# CUSTOMER DELETE
# ADMIN ONLY
# =====================================

@admin_required
def customer_delete(request, pk):

    if request.method == "POST":

        customer = get_object_or_404(Customer, pk=pk)

        try:
            customer_name = customer.customer_name
            customer.delete()

            messages.success(
                request,
                f"{customer_name} deleted successfully."
            )

        except ProtectedError:
            messages.error(
                request,
                "This customer cannot be deleted because sales records are linked to it."
            )

    return redirect("customers:customer_list")


# =====================================
# CUSTOMER CREATE
# ADMIN ONLY
# =====================================

@admin_required
def customer_create(request):

    if request.method == "POST":
        form = CustomerForm(request.POST)

        if form.is_valid():
            customer = form.save()

            messages.success(
                request,
                f"{customer.customer_name} added successfully."
            )

            return redirect("customers:customer_list")

    else:
        form = CustomerForm()

    context = {
        "form": form,
        "page_title": "Add Customer",
        "button_text": "Save Customer",
    }

    return render(
        request,
        "customers/customer_form.html",
        context
    )


# =====================================
# CUSTOMER UPDATE
# ADMIN ONLY
# =====================================

@admin_required
def customer_update(request, pk):

    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            customer = form.save()

            messages.success(
                request,
                f"{customer.customer_name} updated successfully."
            )

            return redirect("customers:customer_list")

    else:
        form = CustomerForm(instance=customer)

    context = {
        "form": form,
        "page_title": "Edit Customer",
        "button_text": "Update Customer",
        "customer": customer,
    }

    return render(
        request,
        "customers/customer_form.html",
        context
    )


# =====================================
# CUSTOMER TOGGLE STATUS
# ADMIN ONLY
# =====================================

@admin_required
def customer_toggle_status(request, pk):

    if request.method == "POST":

        customer = get_object_or_404(Customer, pk=pk)

        customer.is_active = not customer.is_active

        customer.save(update_fields=["is_active", "updated_at"])

        status = "activated" if customer.is_active else "deactivated"

        messages.success(
            request,
            f"{customer.customer_name} {status} successfully."
        )

    return redirect("customers:customer_list")
