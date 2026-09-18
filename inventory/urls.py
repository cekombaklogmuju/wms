from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    # Products
    path("products/", views.product_list, name="product-list"),
    path("products/create/", views.product_create, name="product-create"),
    path("products/<int:pk>/", views.product_detail, name="product-detail"),
    path("products/<int:pk>/update/", views.product_update, name="product-update"),
    path("products/<int:pk>/edit/", views.product_update, name="product-edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product-delete"),
    path("products/<int:pk>/barcode/", views.generate_barcode_view, name="product-barcode"),
    path("products/<int:pk>/qr/", views.generate_qr_view, name="product-qr"),

    # Categories
    path("categories/", views.category_list, name="category-list"),
    path("categories/create/", views.category_create, name="category-create"),
    path("categories/<int:pk>/update/", views.category_update, name="category-update"),
    path("categories/<int:pk>/edit/", views.category_update, name="category-edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category-delete"),

    # Suppliers
    path("suppliers/", views.supplier_list, name="supplier-list"),
    path("suppliers/create/", views.supplier_create, name="supplier-create"),
    path("suppliers/<int:pk>/update/", views.supplier_update, name="supplier-update"),
    path("suppliers/<int:pk>/edit/", views.supplier_update, name="supplier-edit"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier-delete"),

    # Warehouses
    path("warehouses/", views.warehouse_list, name="warehouse-list"),
    path("warehouses/create/", views.warehouse_create, name="warehouse-create"),
    path("warehouses/<int:pk>/", views.warehouse_detail, name="warehouse-detail"),
    path("warehouses/<int:pk>/update/", views.warehouse_update, name="warehouse-update"),
    path("warehouses/<int:pk>/edit/", views.warehouse_update, name="warehouse-edit"),
    path("warehouses/<int:pk>/delete/", views.warehouse_delete, name="warehouse-delete"),

    # Stock
    path("stock/adjust/", views.stock_adjust, name="stock-adjust"),
]
