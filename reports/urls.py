
from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_dashboard, name="reports_dashboard"),

    path(
        "sales/",
        views.detailed_sales_report,
        name="detailed_sales_report",
    ),

    path(
        "purchases/",
        views.detailed_purchase_report,
        name="detailed_purchase_report",
    ),

    path(
        "stock-valuation/",
        views.stock_valuation_report,
        name="stock_valuation_report",
    ),
]
