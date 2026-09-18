from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models import Sum, F, Q, Count
from django.db.models.functions import Coalesce
from django.shortcuts import render

from inventory.models import Product, Warehouse, Stock, StockMovement, Category
from orders.models import InboundOrder, OutboundOrder


@login_required
def stock_report(request):
    stocks = Stock.objects.select_related("product", "warehouse")

    warehouse_id = request.GET.get("warehouse")
    category = request.GET.get("category")
    low_stock_only = request.GET.get("low_stock_only")

    if warehouse_id:
        stocks = stocks.filter(warehouse_id=warehouse_id)

    if category:
        stocks = stocks.filter(product__category_id=category)

    if low_stock_only:
        stocks = stocks.filter(quantity__lte=F("product__reorder_level"))

    warehouses = Warehouse.objects.all()
    categories = Category.objects.all()

    context = {
        "stocks": stocks,
        "warehouses": warehouses,
        "categories": categories,
        "selected_warehouse": warehouse_id,
        "selected_category": category,
        "low_stock_only": low_stock_only,
    }
    return render(request, "reports/stock_report.html", context)


@login_required
def movement_report(request):
    movements = StockMovement.objects.select_related(
        "product", "warehouse", "performed_by"
    ).order_by("-created_at")

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    warehouse_id = request.GET.get("warehouse")
    movement_type = request.GET.get("movement_type")

    if start_date:
        movements = movements.filter(created_at__date__gte=start_date)

    if end_date:
        movements = movements.filter(created_at__date__lte=end_date)

    if warehouse_id:
        movements = movements.filter(warehouse_id=warehouse_id)

    if movement_type:
        movements = movements.filter(movement_type=movement_type)

    paginator = Paginator(movements, 25)
    page = request.GET.get("page")

    try:
        movements_page = paginator.page(page)
    except PageNotAnInteger:
        movements_page = paginator.page(1)
    except EmptyPage:
        movements_page = paginator.page(paginator.num_pages)

    warehouses = Warehouse.objects.all()

    context = {
        "movements": movements_page,
        "warehouses": warehouses,
        "start_date": start_date or "",
        "end_date": end_date or "",
        "selected_warehouse": warehouse_id,
        "selected_movement_type": movement_type,
    }
    return render(request, "reports/movement_report.html", context)


@login_required
def inventory_valuation_report(request):
    products = Product.objects.annotate(
        total_quantity=Coalesce(Sum("stock_records__quantity"), 0),
        total_value=Coalesce(
            Sum(
                F("stock_records__quantity") * F("unit_price"),
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            ),
            0,
            output_field=models.DecimalField(max_digits=14, decimal_places=2),
        ),
    ).order_by("name")

    total_valuation = (
        products.aggregate(
            grand_total=Coalesce(
                Sum("total_value", output_field=models.DecimalField(max_digits=14, decimal_places=2)),
                0,
                output_field=models.DecimalField(max_digits=14, decimal_places=2),
            )
        )["grand_total"]
        or 0
    )

    context = {
        "products": products,
        "total_valuation": total_valuation,
    }
    return render(request, "reports/valuation_report.html", context)


@login_required
def order_report(request):
    inbound_orders = InboundOrder.objects.select_related("supplier", "warehouse").order_by("-created_at")
    outbound_orders = OutboundOrder.objects.select_related("warehouse").order_by("-created_at")

    status_filter = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if status_filter:
        inbound_orders = inbound_orders.filter(status=status_filter)
        outbound_orders = outbound_orders.filter(status=status_filter)

    if start_date:
        inbound_orders = inbound_orders.filter(created_at__date__gte=start_date)
        outbound_orders = outbound_orders.filter(created_at__date__gte=start_date)

    if end_date:
        inbound_orders = inbound_orders.filter(created_at__date__lte=end_date)
        outbound_orders = outbound_orders.filter(created_at__date__lte=end_date)

    inbound_by_status = (
        inbound_orders.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    outbound_by_status = (
        outbound_orders.values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )

    context = {
        "inbound_orders": inbound_orders,
        "outbound_orders": outbound_orders,
        "total_inbound": inbound_orders.count(),
        "total_outbound": outbound_orders.count(),
        "inbound_by_status": inbound_by_status,
        "outbound_by_status": outbound_by_status,
        "selected_status": status_filter,
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "reports/order_report.html", context)
