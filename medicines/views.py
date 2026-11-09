
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import MedicineCategory
from .forms import MedicineCategoryForm


from django.core.paginator import Paginator
from django.db.models import Q


from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q

from .models import Medicine
from .forms import MedicineForm

from .models import MedicineBatch
from .forms import MedicineBatchForm
from datetime import date
from accounts.decorators import admin_required



@login_required
def category_list(request):
    search = request.GET.get("search", "").strip()

    categories = MedicineCategory.objects.all().order_by("name")

    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(categories, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "categories": page_obj,
        "page_obj": page_obj,
        "search": search,
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    # AJAX request: return only the results section
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "medicines/categories/_category_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "medicines/categories/category_list.html",
        context
    )


@admin_required
def category_create(request):
    if request.method == "POST":
        form = MedicineCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect("medicines:category_list")
    else:
        form = MedicineCategoryForm()

    return render(
        request,
        "medicines/categories/category_form.html",
        {"form": form, "page_title": "Add Category"}
    )


@admin_required
def category_update(request, pk):
    category = get_object_or_404(MedicineCategory, pk=pk)

    if request.method == "POST":
        form = MedicineCategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("medicines:category_list")
    else:
        form = MedicineCategoryForm(instance=category)

    return render(
        request,
        "medicines/categories/category_form.html",
        {"form": form, "page_title": "Edit Category"}
    )


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(MedicineCategory, pk=pk)

    if request.method == "POST":
        if category.medicines.exists():
            messages.error(
                request,
                "This category is assigned to medicines and cannot be deleted."
            )
        else:
            category.delete()
            messages.success(request, "Category deleted successfully.")

    return redirect("medicines:category_list")



# =====================================
# MANUFACTURER MANAGEMENT
# =====================================

from django.db.models import Q
from django.db.models.deletion import ProtectedError

from .models import Manufacturer
from .forms import ManufacturerForm



@login_required
def manufacturer_list(request):
    search = request.GET.get("search", "").strip()

    manufacturers = Manufacturer.objects.all().order_by("name")

    # Live Search
    if search:
        manufacturers = manufacturers.filter(
            Q(name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    # Pagination - 10 records per page
    paginator = Paginator(manufacturers, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "manufacturers": page_obj,
        "page_obj": page_obj,
        "search": search,
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    # AJAX Response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "medicines/manufacturers/_manufacturer_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "medicines/manufacturers/manufacturer_list.html",
        context
    )




@admin_required
def manufacturer_create(request):
    if request.method == "POST":
        form = ManufacturerForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Manufacturer added successfully."
            )
            return redirect("medicines:manufacturer_list")
    else:
        form = ManufacturerForm()

    return render(
        request,
        "medicines/manufacturers/manufacturer_form.html",
        {
            "form": form,
            "page_title": "Add Manufacturer",
        }
    )


@admin_required
def manufacturer_update(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)

    if request.method == "POST":
        form = ManufacturerForm(
            request.POST,
            instance=manufacturer
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Manufacturer updated successfully."
            )
            return redirect("medicines:manufacturer_list")
    else:
        form = ManufacturerForm(instance=manufacturer)

    return render(
        request,
        "medicines/manufacturers/manufacturer_form.html",
        {
            "form": form,
            "page_title": "Edit Manufacturer",
        }
    )


@admin_required
def manufacturer_delete(request, pk):
    manufacturer = get_object_or_404(Manufacturer, pk=pk)

    if request.method == "POST":
        try:
            manufacturer.delete()
            messages.success(
                request,
                "Manufacturer deleted successfully."
            )
        except ProtectedError:
            messages.error(
                request,
                "Cannot delete this manufacturer because it is assigned to medicines."
            )

    return redirect("medicines:manufacturer_list")


@admin_required
def manufacturer_toggle_status(request, pk):
    if request.method == "POST":
        manufacturer = get_object_or_404(Manufacturer, pk=pk)

        manufacturer.is_active = not manufacturer.is_active
        manufacturer.save(update_fields=["is_active"])

        status = "activated" if manufacturer.is_active else "deactivated"

        messages.success(
            request,
            f"Manufacturer {status} successfully."
        )

    return redirect("medicines:manufacturer_list")


@admin_required
def category_toggle_status(request, pk):
    if request.method == "POST":
        category = get_object_or_404(MedicineCategory, pk=pk)
        category.is_active = not category.is_active
        category.save(update_fields=["is_active"])

        status = "activated" if category.is_active else "deactivated"
        messages.success(
            request,
            f"Category {status} successfully."
        )

    return redirect("medicines:category_list")



# =====================================
# MEDICINE CREATE VIEW
# =====================================

@admin_required
def medicine_create(request):

    if request.method == "POST":
        form = MedicineForm(request.POST)

        if form.is_valid():
            medicine = form.save()

            messages.success(
                request,
                f"{medicine.name} added successfully."
            )

            return redirect("medicines:medicine_list")

    else:
        form = MedicineForm()

    context = {
        "form": form,
        "page_title": "Add Medicine",
        "button_text": "Save Medicine",
    }

    return render(
        request,
        "medicines/medicine_form.html",
        context
    )


# =====================================
# MEDICINE UPDATE VIEW
# =====================================

@admin_required
def medicine_update(request, pk):

    medicine = get_object_or_404(Medicine, pk=pk)

    if request.method == "POST":
        form = MedicineForm(
            request.POST,
            instance=medicine
        )

        if form.is_valid():
            medicine = form.save()

            messages.success(
                request,
                f"{medicine.name} updated successfully."
            )

            return redirect("medicines:medicine_list")

    else:
        form = MedicineForm(instance=medicine)

    context = {
        "form": form,
        "page_title": "Edit Medicine",
        "button_text": "Update Medicine",
        "medicine": medicine,
    }

    return render(
        request,
        "medicines/medicine_form.html",
        context
    )



# =====================================
# MEDICINE LIST VIEW
# =====================================

@login_required
def medicine_list(request):

    search = request.GET.get("search", "").strip()

    medicines = Medicine.objects.select_related(
        "category",
        "manufacturer"
    ).order_by("name")

    # Live Search
    if search:
        medicines = medicines.filter(
            Q(name__icontains=search) |
            Q(generic_name__icontains=search) |
            Q(barcode__icontains=search) |
            Q(strength__icontains=search) |
            Q(category__name__icontains=search) |
            Q(manufacturer__name__icontains=search)
        )

    # Pagination - 10 records
    paginator = Paginator(medicines, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "medicines": page_obj,
        "page_obj": page_obj,
        "search": search,
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    # AJAX Response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "medicines/medicine_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "medicines/medicine_list.html",
        context
    )


# =====================================
# MEDICINE DELETE VIEW
# =====================================

@admin_required
def medicine_delete(request, pk):

    if request.method == "POST":

        medicine = get_object_or_404(Medicine, pk=pk)

        try:
            medicine_name = medicine.name
            medicine.delete()

            messages.success(
                request,
                f"{medicine_name} deleted successfully."
            )

        except ProtectedError:
            messages.error(
                request,
                "This medicine cannot be deleted because it has existing batches or transactions."
            )

    return redirect("medicines:medicine_list")


# =====================================
# MEDICINE ACTIVATE / DEACTIVATE
# =====================================

@admin_required
def medicine_toggle_status(request, pk):

    if request.method == "POST":

        medicine = get_object_or_404(Medicine, pk=pk)

        medicine.is_active = not medicine.is_active

        medicine.save(update_fields=["is_active"])

        status = "activated" if medicine.is_active else "deactivated"

        messages.success(
            request,
            f"{medicine.name} {status} successfully."
        )

    return redirect("medicines:medicine_list")



# =====================================
# MEDICINE BATCH CREATE
# =====================================

@admin_required
def batch_create(request):

    if request.method == "POST":
        form = MedicineBatchForm(request.POST)

        if form.is_valid():
            batch = form.save()

            messages.success(
                request,
                f"Batch {batch.batch_number} added successfully."
            )

            return redirect("medicines:batch_list")

    else:
        form = MedicineBatchForm()

    context = {
        "form": form,
        "page_title": "Add Medicine Batch",
        "button_text": "Save Batch",
    }

    return render(
        request,
        "medicines/batch_form.html",
        context
    )


# =====================================
# MEDICINE BATCH UPDATE
# =====================================

@admin_required
def batch_update(request, pk):

    batch = get_object_or_404(MedicineBatch, pk=pk)

    if request.method == "POST":
        form = MedicineBatchForm(
            request.POST,
            instance=batch
        )

        if form.is_valid():
            batch = form.save()

            messages.success(
                request,
                f"Batch {batch.batch_number} updated successfully."
            )

            return redirect("medicines:batch_list")

    else:
        form = MedicineBatchForm(instance=batch)

    context = {
        "form": form,
        "page_title": "Edit Medicine Batch",
        "button_text": "Update Batch",
        "batch": batch,
    }

    return render(
        request,
        "medicines/batch_form.html",
        context
    )



# =====================================
# MEDICINE BATCH LIST
# =====================================

@login_required
def batch_list(request):

    search = request.GET.get("search", "").strip()

    batches = MedicineBatch.objects.select_related(
        "medicine"
    ).order_by("expiry_date")

    if search:
        batches = batches.filter(
            Q(medicine__name__icontains=search) |
            Q(batch_number__icontains=search)
        )

    paginator = Paginator(batches, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "batches": page_obj,
        "page_obj": page_obj,
        "search": search,
        "today": date.today(),
        "page_numbers": range(
            max(1, page_obj.number - 2),
            min(paginator.num_pages, page_obj.number + 2) + 1
        ),
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "medicines/batch_results.html",
            context,
            request=request
        )
        return HttpResponse(html)

    return render(
        request,
        "medicines/batch_list.html",
        context
    )


# =====================================
# MEDICINE BATCH DELETE
# =====================================

@admin_required
def batch_delete(request, pk):

    if request.method == "POST":

        batch = get_object_or_404(MedicineBatch, pk=pk)

        try:
            batch_number = batch.batch_number
            batch.delete()

            messages.success(
                request,
                f"Batch {batch_number} deleted successfully."
            )

        except ProtectedError:
            messages.error(
                request,
                "This batch cannot be deleted because it has existing purchase or sales transactions."
            )

    return redirect("medicines:batch_list")



