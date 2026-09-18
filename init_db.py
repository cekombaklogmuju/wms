import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from accounts.models import UserProfile
from inventory.models import Category, Supplier, Warehouse, Product, Stock, StockMovement
from decimal import Decimal

def run_init():
    print("Running migrate...")
    call_command('migrate', interactive=False)
    
    # Create superuser if not exists
    if not User.objects.filter(username='admin').exists():
        print("Creating admin superuser...")
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        profile = getattr(admin, 'profile', None)
        if not profile:
            profile, _ = UserProfile.objects.get_or_create(user=admin)
        profile.role = 'ADMIN'
        profile.save()
        print("Admin user created: admin / admin123")
    else:
        print("Admin user already exists.")

    # Seed sample categories / suppliers / warehouses / products if empty
    if Product.objects.count() == 0:
        print("Seeding initial products...")
        admin = User.objects.get(username='admin')
        c1, _ = Category.objects.get_or_create(name='ATK', defaults={'description': 'Alat Tulis Kantor'})
        c2, _ = Category.objects.get_or_create(name='Aktiva', defaults={'description': 'Peralatan & Aset'})
        c3, _ = Category.objects.get_or_create(name='Elektronik', defaults={'description': 'Peralatan Elektronik'})
        
        s1, _ = Supplier.objects.get_or_create(name='Toko Budhi Cibadak', defaults={'email': 'budhi@cibadak.com'})
        s2, _ = Supplier.objects.get_or_create(name='Jaya Plaza', defaults={'email': 'sales@jayaplaza.com'})
        
        w1, _ = Warehouse.objects.get_or_create(name='MUJU Bandung', defaults={'location': 'MUJU', 'capacity': 10000, 'manager': admin})
        w2, _ = Warehouse.objects.get_or_create(name='MUJU Surabaya', defaults={'location': 'muju-sby', 'capacity': 10000, 'manager': admin})

        items = [
            ('ac', 'AC', c2, s2, Decimal('3000000')),
            ('HVS-A4-75', 'Kertas HVS A4 75 GSM', c1, s1, Decimal('45000')),
            ('HVS-F4', 'Kertas HVS F4 75 GSM', c1, s1, Decimal('50000')),
            ('atk-pulpen', 'Pulpen Gel', c1, s1, Decimal('25000')),
            ('scissor', 'Gunting', c1, s1, Decimal('15000')),
            ('duct-tape', 'Lakban Bening', c1, s1, Decimal('13000')),
            ('id-card', 'Id Card', c1, s1, Decimal('12500')),
            ('TLED42', 'Televisi LED 42"', c3, s2, Decimal('5000000')),
        ]

        for sku, name, cat, sup, price in items:
            cost = (price * Decimal('0.95')).quantize(Decimal('1'))
            p, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'category': cat,
                    'supplier': sup,
                    'unit_price': price,
                    'cost_price': cost,
                    'reorder_level': 10,
                    'is_active': True,
                }
            )
            try:
                p.generate_barcode()
                p.generate_qr_code()
            except Exception:
                pass

            Stock.objects.get_or_create(
                product=p,
                warehouse=w1,
                defaults={'quantity': 50, 'location_in_warehouse': 'Area Utama'}
            )
        print("Products seeded successfully!")

if __name__ == '__main__':
    run_init()
