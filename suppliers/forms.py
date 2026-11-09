
from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier

        fields = [
            "supplier_name",
            "contact_person",
            "phone",
            "alternate_phone",
            "email",
            "gstin",
            "drug_license_number",
            "address",
            "city",
            "state",
            "pincode",
            "opening_balance",
            "is_active",
            "notes",
        ]

        widgets = {
            "supplier_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter supplier name"
            }),

            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter contact person"
            }),

            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter phone number"
            }),

            "alternate_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter alternate phone"
            }),

            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter email address"
            }),

            "gstin": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter GSTIN"
            }),

            "drug_license_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter drug license number"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter full address",
                "rows": 3
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter city"
            }),

            "state": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter state"
            }),

            "pincode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter pincode"
            }),

            "opening_balance": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter opening balance",
                "step": "0.01"
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Additional notes",
                "rows": 3
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError(
                "Enter a valid 10-digit phone number."
            )

        return phone

    def clean_alternate_phone(self):
        phone = self.cleaned_data.get("alternate_phone", "").strip()

        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError(
                "Enter a valid 10-digit alternate phone number."
            )

        return phone
