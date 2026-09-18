from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    # Inbound
    path("inbound/", views.inbound_list, name="inbound-list"),
    path("inbound/create/", views.inbound_create, name="inbound-create"),
    path("inbound/<int:pk>/", views.inbound_detail, name="inbound-detail"),
    path("inbound/<int:pk>/receive/", views.inbound_receive, name="inbound-receive"),

    # Outbound
    path("outbound/", views.outbound_list, name="outbound-list"),
    path("outbound/create/", views.outbound_create, name="outbound-create"),
    path("outbound/<int:pk>/", views.outbound_detail, name="outbound-detail"),
    path("outbound/<int:pk>/process/", views.outbound_process, name="outbound-process"),
    path("outbound/<int:pk>/ship/", views.outbound_ship, name="outbound-ship"),
]
