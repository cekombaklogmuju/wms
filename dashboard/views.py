from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render

from inventory.models import Product, Warehouse, Stock, StockMovement
from orders.models import InboundOrder, OutboundOrder


@login_required
def dashboard_view(request):
    total_products = Product.objects.count()
    total_warehouses = Warehouse.objects.count()

    low_stock_items = Stock.objects.select_related(
        "product", "warehouse"
    ).filter(quantity__lte=F("product__reorder_level"))

    recent_movements = StockMovement.objects.select_related(
        "product", "warehouse", "performed_by"
    ).order_by("-created_at")[:10]

    pending_inbound = InboundOrder.objects.filter(status="PENDING").count()
    pending_outbound = OutboundOrder.objects.filter(status="PENDING").count()

    total_stock_value = (
        Stock.objects.aggregate(
            total_value=Coalesce(
                Sum(
                    F("quantity") * F("product__unit_price"),
                    output_field=models.DecimalField(max_digits=14, decimal_places=2),
                ),
                0,
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            )
        )["total_value"]
        or 0
    )

    stock_by_warehouse = Warehouse.objects.annotate(
        total_stock=Coalesce(Sum("stock_records__quantity"), 0)
    )
    max_stock = max([w.total_stock for w in stock_by_warehouse] or [1]) or 1

    context = {
        "total_products": total_products,
        "total_warehouses": total_warehouses,
        "low_stock_items": low_stock_items,
        "recent_movements": recent_movements,
        "pending_inbound": pending_inbound,
        "pending_outbound": pending_outbound,
        "total_stock_value": total_stock_value,
        "stock_by_warehouse": stock_by_warehouse,
        "max_stock": max_stock,
    }
    return render(request, "dashboard/dashboard.html", context)
