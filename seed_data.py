"""
Production catalog seeder for Grow More.

Setup:
  1. Add Cloudinary credentials to .env using either CLOUDINARY_URL or
     CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET.
  2. Place local images in product_images/ with names like product101.jpg.
  3. Optionally create seed_products.json with a list of product dictionaries.

Execution:
  python seed_data.py
  python seed_data.py --config seed_products.json --images product_images --batch-size 50

The script is intentionally non-destructive. Existing products are skipped by
slug, and each product failure is logged without stopping the whole batch.
"""

import argparse
import json
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "growmore.settings")
django.setup()

from django.db import transaction
from django.utils.text import slugify

from core.models import HeroBanner
from products.cloudinary_utils import CloudinaryUploadError, cloudinary_is_configured, upload_product_image
from products.models import Brand, Category, Product, SizeStock, validate_hex_color


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE_DIR = BASE_DIR / "product_images"


SAMPLE_PRODUCTS = [
    {
        "sku": 101,
        "name": "Aero Linen Camp Shirt",
        "category": "Summer Shirts",
        "brand": "Grow More Original",
        "description": "Lightweight linen blend shirt with an easy resort collar.",
        "price": "1899.00",
        "discount_price": "1599.00",
        "sizes": ["S", "M", "L", "XL"],
        "stock": 24,
        "color_hex": "#3498DB",
        "is_featured": True,
        "is_trending": True,
        "image": "product101.jpg",
    },
    {
        "sku": 102,
        "name": "Coastline Chino Short",
        "category": "Chino Shorts",
        "brand": "Grow More Original",
        "description": "Tailored summer shorts with breathable stretch comfort.",
        "price": "1499.00",
        "sizes": ["M", "L", "XL"],
        "stock": 18,
        "color_hex": "#2ECC71",
        "is_featured": True,
        "image": "product102.jpg",
    },
]


def log_success(message):
    print(f"[OK] {message}")


def log_warning(message):
    print(f"[!] {message}")


def log_error(message):
    print(f"[X] {message}")


def load_products(config_path):
    """Load products from JSON when provided, otherwise use the sample structure."""
    if not config_path:
        return SAMPLE_PRODUCTS

    path = Path(config_path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("Seed config must be a list of product dictionaries.")
    return data


def validate_product_data(data):
    """Validate required product fields before any upload or database write."""
    required = ["name", "category", "description", "price", "sizes", "stock", "color_hex", "image"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    validate_hex_color(data["color_hex"])
    if not isinstance(data["sizes"], list) or not data["sizes"]:
        raise ValueError("sizes must be a non-empty list.")


def resolve_image_path(image_dir, image_name):
    """Locate the product image named in the config."""
    path = Path(image_dir) / image_name
    return path if path.exists() else None


def upload_image_once(image_path, cache):
    """Upload each local image once per run to avoid duplicate Cloudinary uploads."""
    cache_key = str(image_path.resolve())
    if cache_key in cache:
        return cache[cache_key]

    if not cloudinary_is_configured():
        raise CloudinaryUploadError("Cloudinary is not configured in environment variables.")

    with image_path.open("rb") as image_file:
        result = upload_product_image(image_file)
    if not result:
        raise CloudinaryUploadError("Cloudinary upload did not return image metadata.")
    cache[cache_key] = result
    return result


def create_product(data, image_result):
    """Create category, brand, product, and size stock rows in one transaction."""
    slug = data.get("slug") or slugify(data["name"])
    if Product.objects.filter(slug=slug).exists():
        log_warning(f"Product {data.get('sku', slug)} already exists - skipped")
        return False

    with transaction.atomic():
        category, _ = Category.objects.get_or_create(
            name=data["category"],
            defaults={"slug": slugify(data["category"]), "is_active": True},
        )
        brand = None
        if data.get("brand"):
            brand, _ = Brand.objects.get_or_create(
                name=data["brand"],
                defaults={"slug": slugify(data["brand"]), "is_active": True},
            )

        product = Product.objects.create(
            name=data["name"],
            slug=slug,
            category=category,
            brand=brand,
            description=data["description"],
            price=data["price"],
            discount_price=data.get("discount_price") or None,
            sizes=data["sizes"],
            stock=int(data["stock"]),
            color_hex=data["color_hex"].upper(),
            image_url=image_result.secure_url,
            cloudinary_public_id=image_result.public_id,
            is_active=data.get("is_active", True),
            is_featured=data.get("is_featured", False),
            is_trending=data.get("is_trending", False),
        )

        per_size_stock = max(1, int(data["stock"]) // len(data["sizes"]))
        for size in data["sizes"]:
            SizeStock.objects.update_or_create(
                product=product,
                size=size,
                defaults={"stock_quantity": data.get("size_stock", {}).get(size, per_size_stock)},
            )

    log_success(f"Product {data.get('sku', product.id)} created successfully")
    log_success("Image uploaded to Cloudinary")
    log_success("URL saved to database")
    return True


def seed_hero():
    """Create a fallback hero only when the database has none."""
    if HeroBanner.objects.exists():
        return
    HeroBanner.objects.create(
        title="Own The Heat.",
        subtitle="Premium summer menswear for the energetic soul.",
        button_label="Shop Now",
        button_url="/shop/",
        image_url="https://res.cloudinary.com/demo/image/upload/f_auto,q_auto/sample.jpg",
        theme="summer",
        animation_type="scale",
    )
    log_success("Fallback hero banner created")


def process_batch(products, image_dir, batch_size):
    upload_cache = {}
    created = 0
    failed = 0

    for index, data in enumerate(products, start=1):
      if index % batch_size == 1:
          log_success(f"Processing batch starting at item {index}")
      product_ref = data.get("sku") or data.get("name") or index
      try:
          validate_product_data(data)
          image_path = resolve_image_path(image_dir, data["image"])
          if not image_path:
              log_error(f"Product {product_ref} image missing")
              failed += 1
              continue
          image_result = upload_image_once(image_path, upload_cache)
          if create_product(data, image_result):
              created += 1
      except CloudinaryUploadError as exc:
          log_error(f"Product {product_ref} Cloudinary upload failed: {exc}")
          failed += 1
      except Exception as exc:
          log_error(f"Product {product_ref} failed: {exc}")
          failed += 1

    return created, failed


def main():
    parser = argparse.ArgumentParser(description="Seed Grow More products with Cloudinary images.")
    parser.add_argument("--config", help="Path to JSON product config.")
    parser.add_argument("--images", default=str(DEFAULT_IMAGE_DIR), help="Folder containing product images.")
    parser.add_argument("--batch-size", type=int, default=25, help="Batch log interval.")
    args = parser.parse_args()

    products = load_products(args.config)
    created, failed = process_batch(products, Path(args.images), max(1, args.batch_size))
    seed_hero()
    log_success(f"Seed complete: {created} created, {failed} failed")


if __name__ == "__main__":
    main()
