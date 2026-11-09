
from django import forms

from .models import SalePayment


class SalePaymentForm(forms.Form):

    amount = forms.DecimalField(
        label="Payment Amount",
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter payment amount",
            "step": "0.01",
            "min": "0.01",
        }),
    )

    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=SalePayment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
    )

    transaction_reference = forms.CharField(
        label="Transaction Reference",
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "UPI ID / Transaction ID (optional)",
        }),
    )

    notes = forms.CharField(
        label="Notes",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Enter payment notes (optional)",
            "rows": 3,
        }),
    )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]

        if amount <= 0:
            raise forms.ValidationError(
                "Payment amount must be greater than zero."
            )

        return amount
