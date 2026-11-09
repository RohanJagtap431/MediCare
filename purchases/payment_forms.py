
from django import forms

from .models import PurchasePayment


class PurchasePaymentForm(forms.ModelForm):

    class Meta:
        model = PurchasePayment

        fields = [
            "amount",
            "payment_method",
            "transaction_reference",
            "notes",
        ]

        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter payment amount",
                "min": "0.01",
                "step": "0.01",
            }),

            "payment_method": forms.Select(attrs={
                "class": "form-control",
            }),

            "transaction_reference": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter transaction ID (optional)",
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter payment notes (optional)",
                "rows": 3,
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")

        if amount is None or amount <= 0:
            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        return amount
