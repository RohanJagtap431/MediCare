from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("STAFF", "Staff"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="STAFF"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = "ADMIN"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"