from django.db import models


class MedicineCategory(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Medicine Categories"
        
        
class Manufacturer(models.Model):

    name = models.CharField(
        max_length=200,
        unique=True
    )

    contact_person = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        
class Medicine(models.Model):

    DOSAGE_FORM_CHOICES = [
        ("TABLET", "Tablet"),
        ("CAPSULE", "Capsule"),
        ("SYRUP", "Syrup"),
        ("INJECTION", "Injection"),
        ("OINTMENT", "Ointment"),
        ("DROPS", "Drops"),
        ("CREAM", "Cream"),
        ("OTHER", "Other"),
    ]

    name = models.CharField(max_length=200)

    generic_name = models.CharField(
        max_length=200,
        blank=True
    )

    category = models.ForeignKey(
        MedicineCategory,
        on_delete=models.PROTECT,
        related_name="medicines"
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name="medicines",
        null=True,
        blank=True
    )

    strength = models.CharField(
        max_length=100,
        blank=True
    )

    dosage_form = models.CharField(
        max_length=20,
        choices=DOSAGE_FORM_CHOICES,
        default="TABLET"
    )

    pack_size = models.CharField(
        max_length=50,
        blank=True
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    requires_prescription = models.BooleanField(
        default=False
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        
class MedicineBatch(models.Model):

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name="batches"
    )

    batch_number = models.CharField(max_length=100)

    manufacturing_date = models.DateField(
        null=True,
        blank=True
    )

    expiry_date = models.DateField()

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=0)

    minimum_stock_level = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medicine.name} - {self.batch_number}"

    class Meta:
        ordering = ["expiry_date"]

        verbose_name = "Medicine Batch"
        verbose_name_plural = "Medicine Batches"

        constraints = [
            models.UniqueConstraint(
                fields=["medicine", "batch_number"],
                name="unique_medicine_batch"
            )
        ]