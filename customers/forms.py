
from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer

        fields = [
            "customer_name",
            "phone",
            "alternate_phone",
            "email",
            "date_of_birth",
            "gender",
            "address",
            "city",
            "state",
            "pincode",
            "opening_balance",
            "notes",
            "is_active",
        ]

        widgets = {
            "customer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter customer name"
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

            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "gender": forms.Select(attrs={
                "class": "form-control"
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

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Additional notes",
                "rows": 3
            }),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input"
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
