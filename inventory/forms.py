from django import forms

from .models import Category, Product, Stock, StockMovement, Supplier, Warehouse


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "description",
            "category",
            "supplier",
            "unit_price",
            "cost_price",
            "weight",
            "reorder_level",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        is_admin = False
        if user:
            is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'ADMIN')
        if 'cost_price' in self.fields:
            self.fields['cost_price'].required = False
            self.fields['cost_price'].widget.attrs['readonly'] = 'readonly'
            self.fields['cost_price'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['cost_price'].help_text = 'Auto-calculated: 95% of Unit Price (5% profit margin)'
            if not is_admin:
                self.fields['cost_price'].widget = forms.HiddenInput()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = [
            "name",
            "location",
            "address",
            "capacity",
            "manager",
            "is_active",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }


class StockAdjustmentForm(forms.Form):
    ADJUSTMENT_CHOICES = [
        ("ADD", "Add Stock"),
        ("REMOVE", "Remove Stock"),
    ]

    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True))
    warehouse = forms.ModelChoiceField(queryset=Warehouse.objects.filter(is_active=True))
    adjustment_type = forms.ChoiceField(choices=ADJUSTMENT_CHOICES)
    quantity = forms.IntegerField(min_value=1)
    reference = forms.CharField(max_length=100, required=False)
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def clean(self):
        cleaned = super().clean()
        adj_type = cleaned.get("adjustment_type")
        product = cleaned.get("product")
        warehouse = cleaned.get("warehouse")
        quantity = cleaned.get("quantity")

        if adj_type == "REMOVE" and product and warehouse and quantity:
            try:
                stock = Stock.objects.get(product=product, warehouse=warehouse)
            except Stock.DoesNotExist:
                raise forms.ValidationError(
                    "No stock record exists for this product in this warehouse."
                )
            if stock.quantity < quantity:
                raise forms.ValidationError(
                    f"Cannot remove {quantity}. Only {stock.quantity} available."
                )
        return cleaned
