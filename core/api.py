"""
Core API endpoints for dynamic frontend synchronization.
All frontend content is served from these endpoints.
"""

from django.db.models import Q
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
    banners = HeroBanner.objects.filter(is_active=True).order_by("sort_order")
    return JsonResponse(
        {
            "banners": [
                {
                    "id": banner.id,
                    "title": banner.title,
                    "subtitle": banner.subtitle,
                    "button_label": banner.button_label,
                    "button_url": banner.button_url,
                    "image": banner.display_image,
                }
                for banner in banners
            ]
        }
    )


@require_http_methods(["GET"])
def api_products(request):
    query = Product.objects.filter(is_active=True).select_related("category")

    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "featured").strip()

    if q:
        query = query.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))

    if category and category != "all":
        query = query.filter(category__slug=category)

    if request.GET.get("featured") == "true":
        query = query.filter(is_featured=True)

    if request.GET.get("trending") == "true":
        query = query.filter(is_trending=True)

    if sort == "name":
        query = query.order_by("name")
    elif sort in {"price-low", "price-high"}:
        query = list(query)
        query.sort(key=lambda product: product.current_price, reverse=sort == "price-high")

    try:
        limit = int(request.GET.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20
    limit = max(1, min(limit, 100))

    products = query[:limit]
    return JsonResponse({"products": [_serialize_product(product) for product in products], "count": len(products)})


@require_http_methods(["GET"])
def api_product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id, is_active=True)
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
            "colors": product.get_colors_display(),
            "color_hex": product.safe_color_hex,
            "stock": product.stock,
            "is_featured": product.is_featured,
            "is_trending": product.is_trending,
            "main_image": product.main_image_url,
            "gallery_images": product.gallery_images,
            "offer": _serialize_offer(offer) if offer else None,
        }
    )


@require_http_methods(["GET"])
def api_product_offer(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    offer = best_offer_for_product(product)
    return JsonResponse({"offer": _serialize_offer(offer) if offer else None})


@require_http_methods(["GET"])
def api_homepage_sections(request):
    sections = HomepageSection.objects.filter(is_active=True).order_by("sort_order")
    result = []

    for section in sections:
        products = Product.objects.filter(is_active=True).select_related("category")
        if section.section_type == "featured":
            products = products.filter(is_featured=True)
        elif section.section_type == "trending":
            products = products.filter(is_trending=True)

        result.append(
            {
                "id": section.id,
                "title": section.title,
                "section_type": section.section_type,
                "products": [_serialize_product(product) for product in products[: section.limit]],
            }
        )

    return JsonResponse({"sections": result})


@require_http_methods(["GET"])
def api_active_offers(request):
    now = timezone.now()
    offers = PromotionalOffer.objects.filter(is_active=True, starts_at__lte=now, ends_at__gte=now).order_by(
        "display_priority", "-discount_percent"
    )
    return JsonResponse({"offers": [_serialize_offer(offer) for offer in offers if offer.is_current]})


@require_http_methods(["GET"])
def api_offer_detail(request, offer_id):
    offer = get_object_or_404(PromotionalOffer, id=offer_id, is_active=True)
    if not offer.is_current:
        return JsonResponse({"error": "Offer has expired"}, status=404)
    return JsonResponse(_serialize_offer(offer))


@require_http_methods(["GET"])
def api_categories(request):
    categories = Category.objects.filter(is_active=True).order_by("sort_order")
    return JsonResponse(
        {
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                }
                for category in categories
            ]
        }
    )


@require_http_methods(["GET"])
def api_featured_products(request):
    products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:4]
    return JsonResponse({"products": [_serialize_product(product) for product in products]})


@require_http_methods(["GET"])
def api_deal_products(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    deal_products = [product for product in products if best_offer_for_product(product)][:6]
    return JsonResponse({"products": [_serialize_product(product) for product in deal_products]})


@require_http_methods(["GET"])
def api_trending_products(request):
    products = Product.objects.filter(is_active=True, is_trending=True).select_related("category")[:6]
    return JsonResponse({"products": [_serialize_product(product) for product in products]})


def _serialize_product(product):
    offer = best_offer_for_product(product)
    current_price, _ = price_for_product(product)
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category.name,
        "categoryName": product.category.name,
        "category_slug": product.category.slug,
        "description": product.description,
        "desc": product.description,
        "url": product.get_absolute_url(),
        "price": float(current_price),
        "regular_price": float(product.price),
        "current_price": float(current_price),
        "original_price": float(product.original_price),
        "originalPrice": float(product.original_price),
        "discount_percent": product.discount_percent,
        "discountPercent": product.discount_percent,
        "is_featured": product.is_featured,
        "isFeatured": product.is_featured,
        "is_trending": product.is_trending,
        "isTrending": product.is_trending,
        "stock": product.stock,
        "main_image": product.main_image_url,
        "thumbnail": product.main_image_url,
        "images": product.gallery_images,
        "gallery_images": product.gallery_images,
        "sizes": product.sizes,
        "colors": product.get_colors_display(),
        "color_hex": product.safe_color_hex,
        "offer": _serialize_offer(offer) if offer else None,
    }


def _serialize_offer(offer):
    if not offer:
        return None

    return {
        "id": offer.id,
        "title": offer.title,
        "slug": offer.slug,
        "description": offer.description,
        "highlight_text": offer.highlight_text,
        "highlight": offer.highlight_text,
        "offer_label": offer.offer_label,
        "label": offer.offer_label,
        "discount_percent": offer.discount_percent,
        "cta_text": offer.cta_text,
        "cta_link": offer.cta_link,
        "image": offer.display_image,
        "countdown_end": offer.countdown_target.isoformat(),
        "countdown_end_timestamp": int(offer.countdown_target.timestamp() * 1000),
        "endsAt": offer.countdown_target.isoformat(),
        "floating_ball_enabled": offer.floating_ball_enabled,
        "permanent_dismiss_allowed": offer.permanent_dismiss_allowed,
        "display_priority": offer.display_priority,
        "is_current": offer.is_current,
    }
