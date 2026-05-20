from offers.services import active_popup_offer, offer_payload


def active_offer(request):
    offer = active_popup_offer()
    return {
        "active_popup_offer": offer,
        "active_popup_offer_payload": offer_payload(offer),
    }
