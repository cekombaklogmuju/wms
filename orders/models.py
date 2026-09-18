import uuid
from datetime import date

from django.conf import settings
from django.db import models, transaction


class InboundOrder(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RECEIVED", "Received"),
        ("PARTIAL", "Partial"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    supplier = models.ForeignKey(
        "inventory.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inbound_orders_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = date.today().strftime("%Y%m%d")
            uid = uuid.uuid4().hex[:4].upper()
            self.order_number = f"IN-{today}-{uid}"
        super().save(*args, **kwargs)

    @transaction.atomic
    def receive_order(self):
        """Set status RECEIVED, stamp received_date, create/update Stock
        and create StockMovement(type=IN) for every line item."""
        from inventory.models import Stock, StockMovement

        self.status = "RECEIVED"
        self.received_date = date.today()
        self.save()

        for item in self.items.all():
            stock, _created = Stock.objects.get_or_create(
                product=item.product,
                warehouse=self.warehouse,
                defaults={"quantity": 0},
            )
            stock.quantity += item.quantity_received or item.quantity_ordered
            stock.save()

            StockMovement.objects.create(
                product=item.product,
                warehouse=self.warehouse,
                movement_type="IN",
                quantity=item.quantity_received or item.quantity_ordered,
                reference=self.order_number,
            )


class InboundOrderItem(models.Model):
    order = models.ForeignKey(
        InboundOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity_ordered}"


class OutboundOrder(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(max_length=50, unique=True, editable=False)
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    customer_address = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    shipping_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outbound_orders_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = date.today().strftime("%Y%m%d")
            uid = uuid.uuid4().hex[:4].upper()
            self.order_number = f"OUT-{today}-{uid}"
        super().save(*args, **kwargs)

    @transaction.atomic
    def process_order(self):
        """Set status PROCESSING, deduct Stock per item, create
        StockMovement(type=OUT).  Raises ValueError on insufficient stock."""
        from inventory.models import Stock, StockMovement

        for item in self.items.all():
            try:
                stock = Stock.objects.select_for_update().get(
                    product=item.product,
                    warehouse=self.warehouse,
                )
            except Stock.DoesNotExist:
                raise ValueError(
                    f"No stock found for {item.product.name} "
                    f"in {self.warehouse}"
                )

            if stock.quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {item.product.name}: "
                    f"available {stock.quantity}, requested {item.quantity}"
                )

            stock.quantity -= item.quantity
            stock.save()

            StockMovement.objects.create(
                product=item.product,
                warehouse=self.warehouse,
                movement_type="OUT",
                quantity=item.quantity,
                reference=self.order_number,
            )

        self.status = "PROCESSING"
        self.save()

    def ship_order(self):
        """Set status SHIPPED and stamp shipping_date."""
        self.status = "SHIPPED"
        self.shipping_date = date.today()
        self.save()


class OutboundOrderItem(models.Model):
    order = models.ForeignKey(
        OutboundOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey("inventory.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
