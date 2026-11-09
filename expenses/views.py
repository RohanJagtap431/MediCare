
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm


@login_required
def expense_list(request):
    expenses = Expense.objects.select_related(
        "category", "created_by"
    ).all()

    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()

    if search:
        expenses = expenses.filter(
            Q(title__icontains=search)
            | Q(reference_number__icontains=search)
            | Q(category__name__icontains=search)
        )

    if category_id.isdigit():
        expenses = expenses.filter(category_id=int(category_id))

    if start_date:
        try:
            parsed_start = date.fromisoformat(start_date)
            expenses = expenses.filter(expense_date__gte=parsed_start)
        except ValueError:
            start_date = ""

    if end_date:
        try:
            parsed_end = date.fromisoformat(end_date)
            expenses = expenses.filter(expense_date__lte=parsed_end)
        except ValueError:
            end_date = ""

    total_amount = expenses.aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    paginator = Paginator(expenses, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "expenses": page_obj,
        "page_obj": page_obj,
        "categories": ExpenseCategory.objects.filter(is_active=True),
        "search_query": search,
        "selected_category": category_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_amount": total_amount,
        "total_count": expenses.count(),
    }

    return render(request, "expenses/expense_list.html", context)


@login_required
@admin_required
def expense_create(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST, request.FILES)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()

            messages.success(request, "Expense added successfully.")
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm(initial={"expense_date": date.today()})

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "page_title": "Add Expense",
        "button_text": "Save Expense",
    })


@login_required
@admin_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == "POST":
        form = ExpenseForm(
            request.POST,
            request.FILES,
            instance=expense
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully.")
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm(instance=expense)

    return render(request, "expenses/expense_form.html", {
        "form": form,
        "page_title": "Edit Expense",
        "button_text": "Update Expense",
        "expense": expense,
    })


@login_required
@admin_required
@require_POST
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()

    messages.success(request, "Expense deleted successfully.")
    return redirect("expenses:expense_list")


@login_required
def category_list(request):
    categories = ExpenseCategory.objects.all()

    search = request.GET.get("q", "").strip()
    if search:
        categories = categories.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
        )

    paginator = Paginator(categories, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "expenses/category_list.html", {
        "categories": page_obj,
        "page_obj": page_obj,
        "search_query": search,
    })


@login_required
@admin_required
def category_create(request):
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Expense category added successfully.")
            return redirect("expenses:category_list")
    else:
        form = ExpenseCategoryForm()

    return render(request, "expenses/category_form.html", {
        "form": form,
        "page_title": "Add Expense Category",
        "button_text": "Save Category",
    })


@login_required
@admin_required
def category_update(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect("expenses:category_list")
    else:
        form = ExpenseCategoryForm(instance=category)

    return render(request, "expenses/category_form.html", {
        "form": form,
        "page_title": "Edit Expense Category",
        "button_text": "Update Category",
    })


@login_required
@admin_required
@require_POST
def category_toggle(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    category.is_active = not category.is_active
    category.save(update_fields=["is_active"])

    messages.success(
        request,
        "Category status updated successfully."
    )
    return redirect("expenses:category_list")


@login_required
@admin_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    try:
        category.delete()
        messages.success(request, "Category deleted successfully.")
    except ProtectedError:
        messages.error(
            request,
            "This category is already used by expenses. "
            "Deactivate it instead of deleting."
        )

    return redirect("expenses:category_list")
