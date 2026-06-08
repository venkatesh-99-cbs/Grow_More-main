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
        cache.set(cache_key, offers, 300)  # Cache for 5 minutes
    return offers


def active_popup_offer():
    offers = active_offers()
    for offer in offers:
        if offer.show_on_homepage:
            return offer
    return None


def best_offer_for_product(product):
    offers = active_offers()
    best = None
    base_sale_price = product.discount_price or product.price
    best_price = base_sale_price
    for offer in offers:
        if not offer.applies_to_product(product):
            continue
        offer_price = offer.discount_price_for(product.price)
        if offer_price < best_price:
            best = offer
            best_price = offer_price
    return best


def price_for_product(product):
    base_sale_price = product.discount_price or product.price
    offer = best_offer_for_product(product)
    if not offer:
        return base_sale_price, None
    offer_price = offer.discount_price_for(product.price)
    if offer_price < base_sale_price:
        return offer_price, offer
    return base_sale_price, None


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
        "ctaText": offer.cta_text,
        "ctaLink": offer.cta_link,
        "floatingBallEnabled": offer.floating_ball_enabled,
        "permanentDismissAllowed": offer.permanent_dismiss_allowed,
        "image": offer.display_image,
    }
