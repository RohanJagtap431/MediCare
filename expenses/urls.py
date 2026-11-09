
from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.expense_list, name="expense_list"),
    path("add/", views.expense_create, name="expense_create"),
    path("<int:pk>/edit/", views.expense_update, name="expense_update"),
    path("<int:pk>/delete/", views.expense_delete, name="expense_delete"),

    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.category_update,
        name="category_update"
    ),
    path(
        "categories/<int:pk>/toggle/",
        views.category_toggle,
        name="category_toggle"
    ),
    path(
        "categories/<int:pk>/delete/",
        views.category_delete,
        name="category_delete"
    ),
]
