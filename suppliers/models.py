from django.db import models


class Supplier(models.Model):

    supplier_name = models.CharField(max_length=200)

    contact_person = models.CharField(max_length=150, blank=True)

    phone = models.CharField(max_length=15)

    alternate_phone = models.CharField(
        max_length=15,
        blank=True
    )

    email = models.EmailField(blank=True)

    gstin = models.CharField(
        max_length=15,
        blank=True
    )

    drug_license_number = models.CharField(
        max_length=100,
        blank=True
    )

    address = models.TextField(blank=True)

    city = models.CharField(max_length=100, blank=True)

    state = models.CharField(max_length=100, blank=True)

    pincode = models.CharField(max_length=10, blank=True)

    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    is_active = models.BooleanField(default=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.supplier_name

    class Meta:
        ordering = ["supplier_name"]
        verbose_name_plural = "Suppliers"