
from decimal import Decimal

from django import forms

from .models import Expense, ExpenseCategory


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name", "description", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter description",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "category",
            "title",
            "amount",
            "expense_date",
            "payment_method",
            "reference_number",
            "description",
        ]

        widgets = {
            "category": forms.Select(attrs={
                "class": "form-control",
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter expense title",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter amount",
                "step": "0.01",
                "min": "0.01",
            }),
            "expense_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-control",
            }),
            "reference_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Optional reference number",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Optional description",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = ExpenseCategory.objects.filter(is_active=True)

        if self.instance and self.instance.pk:
            categories = (
                ExpenseCategory.objects.filter(is_active=True)
                | ExpenseCategory.objects.filter(
                    pk=self.instance.category_id
                )
            )

        self.fields["category"].queryset = categories.distinct()

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if not amount.is_finite() or amount <= Decimal("0.00"):
            raise forms.ValidationError(
                "Expense amount must be greater than zero."
            )

        return amount

    