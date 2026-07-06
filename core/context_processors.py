from orders.services import get_cart_count_from_session


def cart(request):
    try:
        cart_count = get_cart_count_from_session(request)
        return {"cart": None, "cart_count": cart_count}
    except Exception:
        return {"cart": None, "cart_count": 0}
