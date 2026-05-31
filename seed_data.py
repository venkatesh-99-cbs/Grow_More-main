import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'growmore.settings')
django.setup()

from products.models import Category, Product, Brand, ColorVariant, SizeStock
from core.models import HeroBanner
from django.utils import timezone
from datetime import timedelta

# Clear existing
Product.objects.all().delete()
Category.objects.all().delete()
Brand.objects.all().delete()
ColorVariant.objects.all().delete()
HeroBanner.objects.all().delete()

# Create Categories
cat_shirts = Category.objects.create(name="Summer Shirts", slug="shirts")
cat_shorts = Category.objects.create(name="Chino Shorts", slug="shorts")

# Create Brands
brand_gm = Brand.objects.create(name="Grow More Original", slug="grow-more")

# Create Colors
color_blue = ColorVariant.objects.create(name="Ocean Blue", hex_code="#0066cc")
color_white = ColorVariant.objects.create(name="Pure White", hex_code="#ffffff")

# Create Products
p1 = Product.objects.create(
    name="Linen Breeze Shirt",
    slug="linen-breeze-shirt",
    category=cat_shirts,
    brand=brand_gm,
    description="Breathable linen shirt for hot summer days.",
    price=1999,
    sizes=["S", "M", "L", "XL"],
    is_featured=True,
    image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80"
)
p1.colors.add(color_blue, color_white)

# Add Stock
SizeStock.objects.create(product=p1, size="S", stock_quantity=0)
SizeStock.objects.create(product=p1, size="M", stock_quantity=2)
SizeStock.objects.create(product=p1, size="L", stock_quantity=10)

# Create Hero
HeroBanner.objects.create(
    title="Own The Heat.",
    subtitle="Luxury summer collection now live.",
    button_label="Shop Now",
    button_url="/shop/",
    image_url="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=1600&q=80",
    theme="summer",
    animation_type="scale"
)

print("Seed data created successfully.")
