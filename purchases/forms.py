
from django import forms
from django.db.models import Q

from .models import Purchase
from suppliers.models import Supplier


class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase

        fields = [
            "invoice_number",
            "supplier",
            "purchase_date",
            "discount_amount",
            "notes",
        ]

        widgets = {
            "invoice_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter supplier invoice number"
            }),

            "supplier": forms.Select(attrs={
                "class": "form-control"
            }),

            "purchase_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter discount amount",
                "step": "0.01",
                "min": "0"
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter purchase notes",
                "rows": 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        suppliers = Supplier.objects.filter(is_active=True)

        # Editing existing purchase असल्यास जुना supplier उपलब्ध ठेवा.
        if self.instance and self.instance.pk:
            suppliers = Supplier.objects.filter(
                Q(is_active=True) |
                Q(pk=self.instance.supplier_id)
            )

        self.fields["supplier"].queryset = suppliers.order_by(
            "supplier_name"
        )

    def clean_discount_amount(self):
        discount = self.cleaned_data.get("discount_amount")

        if discount is not None and discount < 0:
            raise forms.ValidationError(
                "Discount cannot be negative."
            )

        return discount


from django.forms import inlineformset_factory
from medicines.models import MedicineBatch
from .models import PurchaseItem


class PurchaseItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseItem

        fields = [
            "batch",
            "quantity",
            "free_quantity",
            "purchase_price",
            "mrp",
            "discount_amount",
            "gst_percentage",
        ]

        widgets = {
            "batch": forms.Select(attrs={
                "class": "form-control"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Enter quantity"
            }),

            "free_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "Free quantity"
            }),

            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Purchase price"
            }),

            "mrp": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "MRP"
            }),

            "discount_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01",
                "placeholder": "Discount amount"
            }),

            "gst_percentage": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "max": "100",
                "step": "0.01",
                "placeholder": "GST %"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["batch"].queryset = (
            MedicineBatch.objects
            .select_related("medicine")
            .order_by("medicine__name", "batch_number")
        )


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
