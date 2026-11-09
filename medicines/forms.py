
from django import forms
from django.db.models import Q

from .models import (
    MedicineCategory,
    Manufacturer,
    Medicine,
)


# =====================================
# MEDICINE CATEGORY FORM
# =====================================

class MedicineCategoryForm(forms.ModelForm):

    class Meta:
        model = MedicineCategory

        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter category name",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter category description",
                "rows": 3,
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


# =====================================
# MANUFACTURER FORM
# =====================================

class ManufacturerForm(forms.ModelForm):

    class Meta:
        model = Manufacturer

        fields = [
            "name",
            "contact_person",
            "phone",
            "email",
            "address",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter manufacturer name",
            }),

            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contact person name",
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter phone number",
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email address",
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter manufacturer address",
                "rows": 3,
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }


# =====================================
# MEDICINE FORM
# =====================================

class MedicineForm(forms.ModelForm):

    class Meta:
        model = Medicine

        fields = [
            "name",
            "generic_name",
            "category",
            "manufacturer",
            "strength",
            "dosage_form",
            "pack_size",
            "barcode",
            "requires_prescription",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter medicine name",
            }),

            "generic_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter generic name",
            }),

            "category": forms.Select(attrs={
                "class": "form-control",
            }),

            "manufacturer": forms.Select(attrs={
                "class": "form-control",
            }),

            "strength": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 500 mg",
            }),

            "dosage_form": forms.Select(attrs={
                "class": "form-control",
            }),

            "pack_size": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Example: 10 tablets",
            }),

            "barcode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter barcode (optional)",
            }),

            "requires_prescription": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter medicine description",
                "rows": 3,
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show only active categories for new medicines.
        # Preserve the existing category while editing.
        category_query = Q(is_active=True)

        if self.instance and self.instance.pk and self.instance.category_id:
            category_query |= Q(pk=self.instance.category_id)

        self.fields["category"].queryset = (
            MedicineCategory.objects.filter(category_query).order_by("name")
        )

        # Show only active manufacturers for new medicines.
        # Preserve the existing manufacturer while editing.
        manufacturer_query = Q(is_active=True)

        if self.instance and self.instance.pk and self.instance.manufacturer_id:
            manufacturer_query |= Q(pk=self.instance.manufacturer_id)

        self.fields["manufacturer"].queryset = (
            Manufacturer.objects.filter(manufacturer_query).order_by("name")
        )

        self.fields["manufacturer"].required = False
        
        
        


# =====================================
# MEDICINE BATCH FORM
# =====================================

from .models import MedicineBatch


class MedicineBatchForm(forms.ModelForm):

    class Meta:
        model = MedicineBatch

        fields = [
            "medicine",
            "batch_number",
            "manufacturing_date",
            "expiry_date",
            "purchase_price",
            "mrp",
            "selling_price",
            "quantity",
            "minimum_stock_level",
        ]

        widgets = {
            "medicine": forms.Select(attrs={
                "class": "form-control",
            }),

            "batch_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter batch number",
            }),

            "manufacturing_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "expiry_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),

            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter purchase price",
                "step": "0.01",
                "min": "0",
            }),

            "mrp": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter MRP",
                "step": "0.01",
                "min": "0",
            }),

            "selling_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter selling price",
                "step": "0.01",
                "min": "0",
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter available quantity",
                "min": "0",
            }),

            "minimum_stock_level": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter minimum stock level",
                "min": "0",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["medicine"].queryset = (
            Medicine.objects.filter(is_active=True).order_by("name")
        )




