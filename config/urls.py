
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("accounts/", include("accounts.urls")),

    # Dashboard
    path("", include("dashboard.urls")),

    # Sales
    path("sales/", include("sales.urls")),

    # Medicines
    path("medicines/", include("medicines.urls")),

    # Suppliers
    path("suppliers/", include("suppliers.urls")),

    # Customers
    path("customers/", include("customers.urls")),

    # Purchases
    path("purchases/", include("purchases.urls")),
    
    path("inventory/", include("inventory.urls")),
    
    path("reports/", include("reports.urls")),
    
    path("expenses/", include("expenses.urls")),
]
