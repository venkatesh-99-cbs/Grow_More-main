from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import HeroBanner, HomepageSection
from offers.models import PromotionalOffer
from products.models import Category, Product


PRODUCTS = [
    ("Aero Linen Camp Shirt", "shirts", 52, "Breathable linen blend with relaxed summer drape.", ["S", "M", "L", "XL"], ["Dusty White", "Bright Blue", "Pink Sand"], ["https://images.unsplash.com/photo-1618886614638-80e3c103d31a?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1622445275576-721325763afe?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80"]),
    ("Coastal Knit Polo", "tees", 48, "Soft knit polo built for humid city days.", ["S", "M", "L", "XL"], ["Blue Green", "Bright Blue", "Dark Sand"], ["https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=80"]),
    ("Sunset Chino Shorts", "shorts", 38, "Tailored fit with stretch comfort for movement.", ["30", "32", "34", "36"], ["Dark Sand", "Dusty White", "Blue Green"], ["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1592878940526-0214b0f374f6?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=80"]),
    ("Wave Runner Tee", "tees", 29, "Ultra-light cotton tee with athletic silhouette.", ["S", "M", "L", "XL"], ["Bright Blue", "Blue Green", "Dusty White"], ["https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=900&q=80"]),
    ("Breeze Utility Overshirt", "outerwear", 64, "Light layer for cooler summer evenings.", ["M", "L", "XL"], ["Dark Sand", "Bright Blue", "Pink Sand"], ["https://images.unsplash.com/photo-1610652492500-ded49ceeb378?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?auto=format&fit=crop&w=900&q=80"]),
    ("Harbor Straw Fedora", "accessories", 24, "Ventilated weave and crisp edge for beach style.", ["One"], ["Dusty White", "Dark Sand"], ["https://images.unsplash.com/photo-1514329926535-7f6db2f2b56a?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1503342394128-c104d54dba01?auto=format&fit=crop&w=900&q=80", "https://images.unsplash.com/photo-1533827432537-70133748f5c8?auto=format&fit=crop&w=900&q=80"]),
]


class Command(BaseCommand):
    help = "Seed the Grow More store with starter products and homepage content."

    def handle(self, *args, **options):
        category_names = {
            "shirts": "Shirts",
            "tees": "Tees",
            "shorts": "Shorts",
            "outerwear": "Outerwear",
            "accessories": "Accessories",
        }
        categories = {}
        for index, (slug, name) in enumerate(category_names.items()):
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": name, "sort_order": index})

        for index, (name, category_slug, price, desc, sizes, colors, images) in enumerate(PRODUCTS):
            Product.objects.update_or_create(
                name=name,
                defaults={
                    "category": categories[category_slug],
                    "description": desc,
                    "price": price,
                    "discount_price": None,
                    "sizes": sizes,
                    "colors": colors,
                    "stock": 25,
                    "is_active": True,
                    "is_featured": index in {0, 1, 2, 4},
                    "is_trending": index in {0, 3, 4},
                    "image_url": images[0],
                    "gallery_url_1": images[1],
                    "gallery_url_2": images[2],
                },
            )

        hero_images = [
            "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=1600&q=80",
            "https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1600&q=80",
        ]
        for index, image in enumerate(hero_images):
            HeroBanner.objects.update_or_create(
                title="Own The Heat. Stay Cool. Move Bold." if index == 0 else f"Summer Energy {index + 1}",
                defaults={
                    "subtitle": "High-energy summer menswear built with breathable fabrics, clean cuts, and ocean-cool color tones.",
                    "button_label": "Explore the Seasons",
                    "button_url": "/shop/",
                    "image_url": image,
                    "sort_order": index,
                    "is_active": True,
                },
            )
        HomepageSection.objects.get_or_create(title="Hero Entry Products", defaults={"section_type": "featured", "limit": 4})
        now = timezone.now()
        offer, _ = PromotionalOffer.objects.update_or_create(
            title="Summer Drop Is Live",
            defaults={
                "description": "Selected summer essentials are live with clean limited-time pricing.",
                "offer_label": "Summer Sale",
                "highlight_text": "Limited premium summer offer",
                "discount_percent": 35,
                "starts_at": now,
                "ends_at": now + timedelta(days=7),
                "countdown_end": now + timedelta(days=7),
                "cta_text": "Shop Deals",
                "cta_link": "/shop/",
                "is_active": True,
                "site_wide": False,
                "show_on_homepage": True,
                "floating_ball_enabled": True,
                "permanent_dismiss_allowed": True,
                "display_priority": 0,
                "offer_type": "trending",
            },
        )
        offer.categories.set([categories["shirts"], categories["tees"]])
        self.stdout.write(self.style.SUCCESS("Grow More starter store seeded."))
