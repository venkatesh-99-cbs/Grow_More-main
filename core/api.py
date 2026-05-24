"""
Core API endpoints for dynamic frontend synchronization.
All frontend content is served from these endpoints.
"""
from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from offers.models import PromotionalOffer
from offers.services import best_offer_for_product, price_for_product
from products.models import Category, Product

from .models import HeroBanner, HomepageSection


@require_http_methods(["GET"])
def api_hero_banners(request):
    """
    GET /api/hero-banners/
    Returns all active hero banners for homepage carousel.
    """
    banners = HeroBanner.objects.filter(is_active=True).order_by("sort_order")
    return JsonResponse(
        {
            "banners": [
                {
                    "id": b.id,
                    "title": b.title,
                    "subtitle": b.subtitle,
                    "button_label": b.button_label,
                    "button_url": b.button_url,
                    "image": b.display_image,
                }
                for b in banners
            ]
        }
    )


@require_http_methods(["GET"])
def api_products(request):
    """
    GET /api/products/
    Returns all active products with current pricing and offer info.

    Query params:
    - category: Filter by category slug
    - featured: true/false filter
    - trending: true/false filter
    - limit: Number of products (default 20)
    """
    query = Product.objects.filter(is_active=True).select_related("category")

    # Filters
    if request.GET.get("category"):
        query = query.filter(category__slug=request.GET.get("category"))

    if request.GET.get("featured") == "true":
        query = query.filter(is_featured=True)

    if request.GET.get("trending") == "true":
        query = query.filter(is_trending=True)

    limit = int(request.GET.get("limit", 20))
    products = query[:limit]

    return JsonResponse(
        {
            "products": [_serialize_product(p) for p in products],
            "count": products.count(),
        }
    )


@require_http_methods(["GET"])
def api_product_detail(request, product_id):
    """
    GET /api/products/{product_id}/
    Returns detailed product info with gallery and current offer.
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)

    offer = best_offer_for_product(product)
    current_price, _ = price_for_product(product)

    return JsonResponse(
        {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "category": {
                "id": product.category.id,
                "name": product.category.name,
                "slug": product.category.slug,
            },
            "description": product.description,
            "price": float(product.price),
            "current_price": float(current_price),
            "original_price": float(product.original_price),
            "discount_percent": product.discount_percent,
            "sizes": product.sizes,
            "colors": product.colors,
            "stock": product.stock,
            "is_featured": product.is_featured,
            "is_trending": product.is_trending,
            "main_image": product.main_image.url if product.main_image else product.image_url,
            "gallery_images": [
            product.gallery_image_1.url if product.gallery_image_1 else product.gallery_url_1,
            product.gallery_image_2.url if product.gallery_image_2 else product.gallery_url_2,
            product.gallery_image_3.url if product.gallery_image_3 else product.gallery_url_3,
            ],
            "offer": _serialize_offer(offer) if offer else None,
        }
    )


@require_http_methods(["GET"])
def api_product_offer(request, product_id):
    """
    GET /api/products/{product_id}/offer/
    Returns current active offer for a product (if any).
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    offer = best_offer_for_product(product)

    if not offer:
        return JsonResponse({"offer": None})

    return JsonResponse(
        {
            "offer": _serialize_offer(offer),
        }
    )


@require_http_methods(["GET"])
def api_homepage_sections(request):
    """
    GET /api/homepage/sections/
    Returns all active homepage sections with their content.
    """
    sections = HomepageSection.objects.filter(is_active=True).order_by("sort_order")
    result = []

    for section in sections:
        if section.section_type == "featured":
            products = Product.objects.filter(is_active=True, is_featured=True)[
                : section.limit
            ]
        elif section.section_type == "trending":
            products = Product.objects.filter(is_active=True, is_trending=True)[
                : section.limit
            ]
        else:  # collection
            products = Product.objects.filter(is_active=True)[: section.limit]

        result.append(
            {
                "id": section.id,
                "title": section.title,
                "section_type": section.section_type,
                "products": [_serialize_product(p) for p in products],
            }
        )

    return JsonResponse({"sections": result})


@require_http_methods(["GET"])
def api_active_offers(request):
    """
    GET /api/offers/active/
    Returns all currently active promotional offers for frontend display.
    """
    now = timezone.now()
    offers = PromotionalOffer.objects.filter(
        is_active=True, starts_at__lte=now, ends_at__gte=now
    ).order_by("display_priority")

    return JsonResponse(
        {
            "offers": [
                {
                    "id": o.id,
                    "title": o.title,
                    "description": o.description,
                    "offer_label": o.offer_label,
                    "discount_percent": o.discount_percent,
                    "cta_text": o.cta_text,
                    "cta_link": o.cta_link,
                    "image": o.display_image.url if o.display_image else "",
                    "countdown_end": o.countdown_target.isoformat(),
                    "floating_ball_enabled": o.floating_ball_enabled,
                    "display_priority": o.display_priority,
                }
                for o in offers
                if o.is_current
            ]
        }
    )


@require_http_methods(["GET"])
def api_offer_detail(request, offer_id):
    """
    GET /api/offers/{offer_id}/
    Returns detailed offer information.
    """
    offer = get_object_or_404(PromotionalOffer, id=offer_id, is_active=True)

    if not offer.is_current:
        return JsonResponse({"error": "Offer has expired"}, status=404)

    return JsonResponse(_serialize_offer(offer))


@require_http_methods(["GET"])
def api_categories(request):
    """
    GET /api/categories/
    Returns all active product categories.
    """
    categories = Category.objects.filter(is_active=True).order_by("sort_order")
    return JsonResponse(
        {
            "categories": [
                {
                    "id": c.id,
                    "name": c.name,
                    "slug": c.slug,
                    "description": c.description,
                }
                for c in categories
            ]
        }
    )


@require_http_methods(["GET"])
def api_featured_products(request):
    """
    GET /api/featured-products/
    Returns featured products for display sections.
    """
    products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    return JsonResponse(
        {
            "products": [_serialize_product(p) for p in products],
        }
    )


@require_http_methods(["GET"])
def api_deal_products(request):
    """
    GET /api/deal-products/
    Returns products with active offers (deals).
    """
    now = timezone.now()
    offers = PromotionalOffer.objects.filter(
        is_active=True, starts_at__lte=now, ends_at__gte=now
    ).values_list("products__id", flat=True)

    products = Product.objects.filter(is_active=True, id__in=offers)[:6]
    return JsonResponse(
        {
            "products": [_serialize_product(p) for p in products],
        }
    )


@require_http_methods(["GET"])
def api_trending_products(request):
    """
    GET /api/trending-products/
    Returns trending products.
    """
    products = Product.objects.filter(is_active=True, is_trending=True)[:6]
    return JsonResponse(
        {
            "products": [_serialize_product(p) for p in products],
        }
    )


# ============================================================================
# Helper serializers
# ============================================================================


def _serialize_product(product):
    """Serialize product to API JSON format."""
    offer = best_offer_for_product(product)
    current_price, _ = price_for_product(product)
    
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category.name,
        "category_slug": product.category.slug,
        "description": product.description,
        "price": float(product.price),
        "current_price": float(current_price),
        "original_price": float(product.original_price),
        "discount_percent": product.discount_percent,
        "is_featured": product.is_featured,
        "is_trending": product.is_trending,
        "stock": product.stock,
        "main_image": product.main_image.url if product.main_image else product.image_url,
        "thumbnail": product.main_image.url if product.main_image else product.image_url,
        "images": [
            product.main_image.url or product.image_url,
            product.gallery_image_1.url or product.gallery_url_1 or "",
            product.gallery_image_2.url or product.gallery_url_2 or "",
            product.gallery_image_3.url or product.gallery_url_3 or "",
        ],
        "gallery_images": [
            product.main_image.url or product.image_url,
            product.gallery_image_1.url if product.gallery_image_1 else product.gallery_url_1,
            product.gallery_image_2.url if product.gallery_image_2 else product.gallery_url_2,
            product.gallery_image_3.url if product.gallery_image_3 else product.gallery_url_3,
       ],

        "sizes": product.sizes,
        "colors": product.colors,
        "offer": _serialize_offer(offer) if offer else None,
    }
def _serialize_product(product):
    """Serialize product to API JSON format."""
    offer = best_offer_for_product(product)
    current_price, _ = price_for_product(product)
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category.name,
        "category_slug": product.category.slug,
        "description": product.description,
        "price": float(product.price),
        "current_price": float(current_price),
        "original_price": float(product.original_price),
        "discount_percent": product.discount_percent,
        "is_featured": product.is_featured,
        "is_trending": product.is_trending,
        "stock": product.stock,
        # Safe access to main_image: check if object exists before .url
        "main_image": product.main_image.url if product.main_image else product.image_url,
        "thumbnail": product.main_image.url if product.main_image else product.image_url,
        "images": [
            product.main_image.url if product.main_image else product.image_url,
            product.gallery_image_1.url if product.gallery_image_1 else product.gallery_url_1 or "",
            product.gallery_image_2.url if product.gallery_image_2 else product.gallery_url_2 or "",
            product.gallery_image_3.url if product.gallery_image_3 else product.gallery_url_3 or "",
        ],
        "gallery_images": [
            product.main_image.url if product.main_image else product.image_url,
            product.gallery_image_1.url if product.gallery_image_1 else product.gallery_url_1,
            product.gallery_image_2.url if product.gallery_image_2 else product.gallery_url_2,
            product.gallery_image_3.url if product.gallery_image_3 else product.gallery_url_3,
        ],
        "sizes": product.sizes,
        "colors": product.colors,
        "offer": _serialize_offer(offer) if offer else None,
    }

def _serialize_offer(offer):
    """Serialize offer to API JSON format."""
    if not offer:
        return None

    return {
        "id": offer.id,
        "title": offer.title,
        "slug": offer.slug,
        "description": offer.description,
        "offer_label": offer.offer_label,
        "discount_percent": offer.discount_percent,
        "cta_text": offer.cta_text,
        "cta_link": offer.cta_link,
        "image": offer.display_image,
        "countdown_end": offer.countdown_target.isoformat(),
        "countdown_end_timestamp": int(offer.countdown_target.timestamp() * 1000),
        "floating_ball_enabled": offer.floating_ball_enabled,
        "permanent_dismiss_allowed": offer.permanent_dismiss_allowed,
        "display_priority": offer.display_priority,
        "is_current": offer.is_current,
    }
