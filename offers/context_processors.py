from offers.services import active_popup_offer, offer_payload


def active_offer(request):
    offer = active_popup_offer()
    payload = offer_payload(offer)
    return {
        "active_popup_offer": offer,
        "active_popup_offer_payload": payload,
        "offer_end_ms": payload.get("offer_end_ms", 0) if payload else 0,
    }
