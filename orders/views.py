from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    InboundOrderForm,
    InboundOrderItemFormSet,
    OutboundOrderForm,
    OutboundOrderItemFormSet,
)
from .models import InboundOrder, OutboundOrder


# ---------------------------------------------------------------------------
# Inbound Orders
# ---------------------------------------------------------------------------

@login_required
def inbound_list(request):
    queryset = InboundOrder.objects.select_related("supplier", "warehouse")

    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "orders/inbound_list.html", {
        "page_obj": page,
        "selected_status": status,
        "status_choices": InboundOrder.STATUS_CHOICES,
    })


@login_required
def inbound_detail(request, pk):
    order = get_object_or_404(
        InboundOrder.objects.select_related("supplier", "warehouse", "created_by"),
        pk=pk,
    )
    items = order.items.select_related("product")
    return render(request, "orders/inbound_detail.html", {
        "order": order,
        "items": items,
    })


@login_required
def inbound_create(request):
    if request.method == "POST":
        form = InboundOrderForm(request.POST)
        formset = InboundOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            formset.instance = order
            formset.save()
            messages.success(
                request,
                f"Inbound order '{order.order_number}' created.",
            )
            return redirect("orders:inbound-detail", pk=order.pk)
    else:
        form = InboundOrderForm()
        formset = InboundOrderItemFormSet()
    return render(request, "orders/inbound_form.html", {
        "form": form,
        "formset": formset,
    })


@login_required
def inbound_receive(request, pk):
    order = get_object_or_404(InboundOrder, pk=pk)
    if request.method == "POST":
        try:
            order.receive_order()
            messages.success(
                request,
                f"Order '{order.order_number}' received. Stock updated.",
            )
        except Exception as exc:
            messages.error(request, f"Error receiving order: {exc}")
    return redirect("orders:inbound-detail", pk=order.pk)


# ---------------------------------------------------------------------------
# Outbound Orders
# ---------------------------------------------------------------------------

@login_required
def outbound_list(request):
    queryset = OutboundOrder.objects.select_related("warehouse")

    status = request.GET.get("status")
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 20)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "orders/outbound_list.html", {
        "page_obj": page,
        "selected_status": status,
        "status_choices": OutboundOrder.STATUS_CHOICES,
    })


@login_required
def outbound_detail(request, pk):
    order = get_object_or_404(
        OutboundOrder.objects.select_related("warehouse", "created_by"),
        pk=pk,
    )
    items = order.items.select_related("product")
    return render(request, "orders/outbound_detail.html", {
        "order": order,
        "items": items,
    })


@login_required
def outbound_create(request):
    if request.method == "POST":
        form = OutboundOrderForm(request.POST)
        formset = OutboundOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            formset.instance = order
            formset.save()
            messages.success(
                request,
                f"Outbound order '{order.order_number}' created.",
            )
            return redirect("orders:outbound-detail", pk=order.pk)
    else:
        form = OutboundOrderForm()
        formset = OutboundOrderItemFormSet()
    return render(request, "orders/outbound_form.html", {
        "form": form,
        "formset": formset,
    })


@login_required
def outbound_process(request, pk):
    order = get_object_or_404(OutboundOrder, pk=pk)
    if request.method == "POST":
        try:
            order.process_order()
            messages.success(
                request,
                f"Order '{order.order_number}' processed. Stock deducted.",
            )
        except ValueError as exc:
            messages.error(request, f"Cannot process order: {exc}")
        except Exception as exc:
            messages.error(request, f"Error processing order: {exc}")
    return redirect("orders:outbound-detail", pk=order.pk)


@login_required
def outbound_ship(request, pk):
    order = get_object_or_404(OutboundOrder, pk=pk)
    if request.method == "POST":
        try:
            order.ship_order()
            messages.success(
                request,
                f"Order '{order.order_number}' shipped.",
            )
        except Exception as exc:
            messages.error(request, f"Error shipping order: {exc}")
    return redirect("orders:outbound-detail", pk=order.pk)
