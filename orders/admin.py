from django.contrib import admin

from .models import (
    InboundOrder,
    InboundOrderItem,
    OutboundOrder,
    OutboundOrderItem,
)


class InboundOrderItemInline(admin.TabularInline):
    model = InboundOrderItem
    extra = 1
    fields = ("product", "quantity_ordered", "quantity_received", "unit_cost")


@admin.register(InboundOrder)
class InboundOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "supplier",
        "warehouse",
        "status",
        "expected_date",
        "received_date",
        "created_at",
    )
    list_filter = ("status", "warehouse", "created_at")
    search_fields = ("order_number", "supplier__name")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [InboundOrderItemInline]


class OutboundOrderItemInline(admin.TabularInline):
    model = OutboundOrderItem
    extra = 1
    fields = ("product", "quantity", "unit_price")


@admin.register(OutboundOrder)
class OutboundOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "warehouse",
        "status",
        "shipping_date",
        "delivery_date",
        "created_at",
    )
    list_filter = ("status", "warehouse", "created_at")
    search_fields = ("order_number", "customer_name")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OutboundOrderItemInline]
