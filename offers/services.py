from decimal import Decimal

from django.core.cache import cache
from django.utils import timezone

from offers.models import PromotionalOffer


def active_offers():
    now = timezone.now()
    return (
        PromotionalOffer.objects.filter(is_active=True, starts_at__lte=now, ends_at__gte=now)
        .prefetch_related("products", "categories")
        .order_by("display_priority", "-discount_percent")
    )


def active_popup_offer():
    return active_offers().filter(show_on_homepage=True).first()


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
