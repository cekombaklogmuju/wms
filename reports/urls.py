from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("stock/", views.stock_report, name="stock_report"),
    path("movements/", views.movement_report, name="movement_report"),
    path("valuation/", views.inventory_valuation_report, name="valuation_report"),
    path("orders/", views.order_report, name="order_report"),
]
