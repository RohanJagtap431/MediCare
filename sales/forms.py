
from datetime import date

from django import forms
from django.forms import inlineformset_factory

from .models import Sale, SaleItem
from customers.models import Customer
from medicines.models import MedicineBatch


class SaleForm(forms.ModelForm):

    class Meta:
        model = Sale
        fields = [
            "customer",
            "discount_amount",
            "notes",
        ]

        widgets = {
            "customer": forms.Select(attrs={
                "class": "form-control",
            }),
            "discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter bill notes (optional)",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["customer"].queryset = (
            Customer.objects.filter(is_active=True)
            .order_by("customer_name")
        )

        self.fields["customer"].required = False

    def clean_discount_amount(self):
        discount = self.cleaned_data.get("discount_amount") or 0

        if discount < 0:
            raise forms.ValidationError(
                "Discount cannot be negative."
            )

        return discount


class SaleItemForm(forms.ModelForm):

    class Meta:
        model = SaleItem
        fields = [
            "batch",
            "quantity",
            "selling_price",
            "discount_amount",
            "gst_percentage",
        ]

        widgets = {
            "batch": forms.Select(attrs={
                "class": "form-control batch-select",
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
            }),
            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
            "discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
            "gst_percentage": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["batch"].queryset = (
            MedicineBatch.objects
            .filter(
                quantity__gt=0,
                expiry_date__gte=date.today()
            )
            .select_related("medicine")
            .order_by("medicine__name", "expiry_date")
        )

        self.fields["batch"].label_from_instance = (
            lambda batch: (
                f"{batch.medicine.name} | "
                f"Batch: {batch.batch_number} | "
                f"Stock: {batch.quantity}"
            )
        )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero."
            )

        return quantity


SaleItemFormSet = inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
