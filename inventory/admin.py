from django.contrib import admin

from .models import Category, Product, Stock, StockMovement, Supplier, Warehouse


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "email", "phone", "created_at")
    search_fields = ("name", "contact_person", "email")
    list_filter = ("created_at",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity", "manager", "is_active", "created_at")
    search_fields = ("name", "location", "address")
    list_filter = ("is_active", "created_at")
    raw_id_fields = ("manager",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "supplier",
        "unit_price",
        "cost_price",
        "reorder_level",
        "is_active",
    )
    search_fields = ("sku", "name", "barcode", "description")
    list_filter = ("is_active", "category", "supplier", "created_at")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("category", "supplier")
    actions = ["generate_barcodes", "generate_qr_codes"]

    @admin.action(description="Generate barcodes for selected products")
    def generate_barcodes(self, request, queryset):
        for product in queryset:
            product.generate_barcode()
        self.message_user(request, f"Barcodes generated for {queryset.count()} products.")

    @admin.action(description="Generate QR codes for selected products")
    def generate_qr_codes(self, request, queryset):
        for product in queryset:
            product.generate_qr_code()
        self.message_user(request, f"QR codes generated for {queryset.count()} products.")


class LowStockFilter(admin.SimpleListFilter):
    title = "stock level"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return [
            ("low", "Low Stock"),
            ("ok", "Adequate Stock"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(quantity__lte=models.F("product__reorder_level"))
        if self.value() == "ok":
            return queryset.filter(quantity__gt=models.F("product__reorder_level"))
        return queryset


from django.db import models as db_models  # noqa: E402 (needed for F expression)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "warehouse",
        "quantity",
        "location_in_warehouse",
        "is_low_stock_display",
        "last_checked",
    )
    search_fields = ("product__name", "product__sku", "warehouse__name", "location_in_warehouse")
    list_filter = ("warehouse", "last_checked")
    raw_id_fields = ("product", "warehouse")

    @admin.display(boolean=True, description="Low Stock?")
    def is_low_stock_display(self, obj):
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "warehouse",
        "movement_type",
        "quantity",
        "reference",
        "performed_by",
        "created_at",
    )
    search_fields = ("product__name", "product__sku", "reference", "notes")
    list_filter = ("movement_type", "warehouse", "created_at")
    raw_id_fields = ("product", "warehouse", "performed_by")
    readonly_fields = ("created_at",)
