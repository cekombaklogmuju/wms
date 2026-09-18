import io

import barcode
from barcode.writer import ImageWriter
import qrcode
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CategoryForm,
    ProductForm,
    StockAdjustmentForm,
    SupplierForm,
    WarehouseForm,
)
from .models import Category, Product, Stock, StockMovement, Supplier, Warehouse


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@login_required
def product_list(request):
    queryset = Product.objects.select_related("category", "supplier")

    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(sku__icontains=query)
            | Q(barcode__icontains=query)
        )

    category_id = request.GET.get("category")
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    paginator = Paginator(queryset, 20)
    page = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all()
    return render(request, "inventory/product_list.html", {
        "page_obj": page,
        "query": query,
        "categories": categories,
        "selected_category": category_id,
    })


@login_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category", "supplier"), pk=pk
    )
    stock_levels = Stock.objects.filter(product=product).select_related("warehouse")
    return render(request, "inventory/product_detail.html", {
        "product": product,
        "stock_levels": stock_levels,
    })


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            if product.unit_price:
                from decimal import Decimal
                product.cost_price = (product.unit_price * Decimal('0.95')).quantize(Decimal('1'))
            product.save()
            product.generate_barcode()
            product.generate_qr_code()
            messages.success(request, f"Product '{product.name}' created.")
            return redirect("inventory:product-detail", pk=product.pk)
    else:
        form = ProductForm(user=request.user)
    return render(request, "inventory/product_form.html", {"form": form})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            if product.unit_price:
                from decimal import Decimal
                product.cost_price = (product.unit_price * Decimal('0.95')).quantize(Decimal('1'))
            product.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect("inventory:product-detail", pk=product.pk)
    else:
        form = ProductForm(instance=product, user=request.user)
    return render(request, "inventory/product_form.html", {
        "form": form,
        "product": product,
    })


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
        return redirect("inventory:product-list")
    return render(request, "inventory/product_confirm_delete.html", {
        "product": product,
    })


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "inventory/category_list.html", {
        "categories": categories,
    })


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created.")
            return redirect("inventory:category-list")
    else:
        form = CategoryForm()
    return render(request, "inventory/category_form.html", {"form": form})


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect("inventory:category-list")
    else:
        form = CategoryForm(instance=category)
    return render(request, "inventory/category_form.html", {
        "form": form,
        "category": category,
    })


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = category.name
        category.delete()
        messages.success(request, f"Category '{name}' deleted.")
        return redirect("inventory:category-list")
    return render(request, "inventory/category_confirm_delete.html", {
        "category": category,
    })


# ---------------------------------------------------------------------------
# Suppliers
# ---------------------------------------------------------------------------

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "inventory/supplier_list.html", {
        "suppliers": suppliers,
    })


@login_required
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f"Supplier '{supplier.name}' created.")
            return redirect("inventory:supplier-list")
    else:
        form = SupplierForm()
    return render(request, "inventory/supplier_form.html", {"form": form})


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f"Supplier '{supplier.name}' updated.")
            return redirect("inventory:supplier-list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "inventory/supplier_form.html", {
        "form": form,
        "supplier": supplier,
    })


@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        name = supplier.name
        supplier.delete()
        messages.success(request, f"Supplier '{name}' deleted.")
        return redirect("inventory:supplier-list")
    return render(request, "inventory/supplier_confirm_delete.html", {
        "supplier": supplier,
    })


# ---------------------------------------------------------------------------
# Warehouses
# ---------------------------------------------------------------------------

@login_required
def warehouse_list(request):
    warehouses = Warehouse.objects.all()
    return render(request, "inventory/warehouse_list.html", {
        "warehouses": warehouses,
    })


@login_required
def warehouse_detail(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    stock_records = (
        Stock.objects.filter(warehouse=warehouse)
        .select_related("product")
    )
    return render(request, "inventory/warehouse_detail.html", {
        "warehouse": warehouse,
        "stock_records": stock_records,
    })


@login_required
def warehouse_create(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save()
            messages.success(request, f"Warehouse '{warehouse.name}' created.")
            return redirect("inventory:warehouse-list")
    else:
        form = WarehouseForm()
    return render(request, "inventory/warehouse_form.html", {"form": form})


@login_required
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, f"Warehouse '{warehouse.name}' updated.")
            return redirect("inventory:warehouse-list")
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, "inventory/warehouse_form.html", {
        "form": form,
        "warehouse": warehouse,
    })


@login_required
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == "POST":
        name = warehouse.name
        warehouse.delete()
        messages.success(request, f"Warehouse '{name}' deleted.")
        return redirect("inventory:warehouse-list")
    return render(request, "inventory/warehouse_confirm_delete.html", {
        "warehouse": warehouse,
    })


# ---------------------------------------------------------------------------
# Stock Adjustment
# ---------------------------------------------------------------------------

@login_required
def stock_adjust(request):
    if request.method == "POST":
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            warehouse = form.cleaned_data["warehouse"]
            adj_type = form.cleaned_data["adjustment_type"]
            quantity = form.cleaned_data["quantity"]
            reference = form.cleaned_data["reference"]
            notes = form.cleaned_data["notes"]

            stock, _created = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={"quantity": 0},
            )

            if adj_type == "ADD":
                stock.quantity += quantity
                movement_type = "IN"
            else:
                stock.quantity -= quantity
                movement_type = "OUT"

            stock.save()

            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type=movement_type,
                quantity=quantity,
                reference=reference,
                notes=notes,
                performed_by=request.user,
            )

            messages.success(
                request,
                f"Stock adjusted: {adj_type} {quantity} of '{product.name}' "
                f"at {warehouse.name}.",
            )
            return redirect("inventory:stock-adjust")
    else:
        form = StockAdjustmentForm()
    return render(request, "inventory/stock_adjust.html", {"form": form})


# ---------------------------------------------------------------------------
# Barcode / QR generation (image responses)
# ---------------------------------------------------------------------------

@login_required
def generate_barcode_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    code128 = barcode.get("code128", product.sku, writer=ImageWriter())
    buffer = io.BytesIO()
    code128.write(buffer)
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required
def generate_qr_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"SKU:{product.sku}|Name:{product.name}|Price:{product.unit_price}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")
