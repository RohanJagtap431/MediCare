from django.db import models


class ShopProfile(models.Model):

    shop_name = models.CharField(max_length=200)

    owner_name = models.CharField(max_length=150)

    phone = models.CharField(max_length=15)

    email = models.EmailField(blank=True)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=10)

    gstin = models.CharField(
        max_length=15,
        blank=True
    )

    drug_license_number = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name

    class Meta:
        verbose_name = "Shop Profile"
        verbose_name_plural = "Shop Profile"