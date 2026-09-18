from django import forms
from django.forms import inlineformset_factory

from inventory.models import Product
from .models import (
    InboundOrder,
    InboundOrderItem,
    OutboundOrder,
    OutboundOrderItem,
)


class InboundOrderForm(forms.ModelForm):
    class Meta:
        model = InboundOrder
        fields = ["supplier", "warehouse", "expected_date", "notes"]
        widgets = {
            "expected_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class InboundOrderItemForm(forms.ModelForm):
    class Meta:
        model = InboundOrderItem
        fields = ["product", "quantity_ordered", "quantity_received", "unit_cost"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)


InboundOrderItemFormSet = inlineformset_factory(
    InboundOrder,
    InboundOrderItem,
    form=InboundOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


class OutboundOrderForm(forms.ModelForm):
    class Meta:
        model = OutboundOrder
        fields = [
            "warehouse",
            "customer_name",
            "customer_address",
            "notes",
        ]
        widgets = {
            "customer_address": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class OutboundOrderItemForm(forms.ModelForm):
    class Meta:
        model = OutboundOrderItem
        fields = ["product", "quantity", "unit_price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True)


OutboundOrderItemFormSet = inlineformset_factory(
    OutboundOrder,
    OutboundOrderItem,
    form=OutboundOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
