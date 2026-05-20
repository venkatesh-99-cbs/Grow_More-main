from django.http import JsonResponse

from offers.services import active_offers, active_popup_offer, offer_payload


def active_offer_api(request):
    popup_offer = active_popup_offer()
    return JsonResponse(
        {
            "popupOffer": offer_payload(popup_offer),
            "offers": [offer_payload(offer) for offer in active_offers()],
        }
    )
