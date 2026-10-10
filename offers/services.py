from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

from offers.models import PromotionalOffer


def active_offers():
    cache_key = "active_promotional_offers"
    offers = cache.get(cache_key)
    if offers is None:
        now = timezone.now()
        offers = list(
            PromotionalOffer.objects.filter(is_active=True, starts_at__lte=now, ends_at__gte=now)
            .prefetch_related("products", "categories", "brands")
            .order_by("display_priority", "-discount_percent")
        )
        # Pre-calculate sets for O(1) lookup in applies_to_product
        # Using .all() to leverage prefetched data and avoid N+1 queries
        for offer in offers:
            if offer.offer_type == "product":
                offer._product_ids = {p.pk for p in offer.products.all()}
            elif offer.offer_type == "category":
                offer._category_ids = {c.pk for c in offer.categories.all()}
            elif offer.offer_type == "brand":
                offer._brand_ids = {b.pk for b in offer.brands.all()}

        cache.set(cache_key, offers, 300)  # Cache for 5 minutes
    return offers


def active_popup_offer():
    offers = active_offers()
    for offer in offers:
        if offer.show_on_homepage:
            return offer
    return None


def best_offer_for_product(product):
    """
    Find the highest priority active offer that provides a better discount
    than the product's manual discount_price.
    """
    offers = active_offers()
    base_sale_price = product.discount_price or product.price

    best_offer = None
    best_price = base_sale_price

    for offer in offers:
        if offer.applies_to_product(product):
            offer_price = offer.discount_price_for(product.price)
            # If this offer is better than or equal to current best (including manual discount)
            # Admin created offers take precedence.
            if offer_price <= best_price:
                best_price = offer_price
                best_offer = offer

            # Since active_offers() is sorted by priority, if we found an offer
            # that is better than the manual discount, we should stick with priority
            # unless a lower priority offer is EVEN better?
            # For now, we take the absolute best price among all applicable offers.

    return best_offer


def price_for_product(product):
    """Returns (current_price, applied_offer_object)"""
    offer = best_offer_for_product(product)
    if offer:
        return offer.discount_price_for(product.price), offer

    if product.discount_price:
        return product.discount_price, None

    return product.price, None


def offer_payload(offer):
    if not offer:
        return None
    return {
        "id": offer.id,
        "title": offer.title,
        "description": offer.description,
        "label": offer.offer_label,
        "highlight": offer.highlight_text,
        "discountPercent": offer.discount_percent,
        "endsAt": offer.countdown_target.isoformat(),
        "offer_end_ms": int(offer.countdown_target.timestamp() * 1000),
        "ctaText": offer.cta_text,
        "ctaLink": offer.cta_link,
        "floatingBallEnabled": offer.floating_ball_enabled,
        "permanentDismissAllowed": offer.permanent_dismiss_allowed,
        "image": offer.display_image,
    }


def get_products_with_active_offers(limit=6):
    """
    Get a list of active products that have an active offer.
    Uses DB-level filtering to avoid N+1 queries.
    """
    from django.db.models import Q
    from products.models import Product

    offers = active_offers()
    if not offers:
        return Product.objects.none()

    # Check if there is any site-wide active offer. If so, all products are discounted!
    has_site_wide = any(o.offer_type == 'site_wide' for o in offers)
    if has_site_wide:
        return Product.objects.filter(is_active=True).order_by('-is_featured', '-is_trending').select_related("category")[:limit]

    # Build Q filters for targeted offers
    product_pks = set()
    category_ids = set()
    brand_ids = set()
    featured_offers = False
    trending_offers = False

    for offer in offers:
        if offer.offer_type == 'product':
            product_pks.update(offer.products.values_list('pk', flat=True))
        elif offer.offer_type == 'category':
            category_ids.update(offer.categories.values_list('pk', flat=True))
        elif offer.offer_type == 'brand':
            brand_ids.update(offer.brands.values_list('pk', flat=True))
        elif offer.offer_type == 'homepage':
            featured_offers = True
        elif offer.offer_type == 'trending':
            trending_offers = True

    q_filter = Q(pk__in=product_pks)
    if category_ids:
        q_filter |= Q(category_id__in=category_ids)
    if brand_ids:
        q_filter |= Q(brand_id__in=brand_ids)
    if featured_offers:
        q_filter |= Q(is_featured=True)
    if trending_offers:
        q_filter |= Q(is_trending=True)

    return Product.objects.filter(is_active=True).filter(q_filter).select_related("category").distinct()[:limit]
