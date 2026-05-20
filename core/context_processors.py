from orders.services import get_or_create_cart


def cart(request):
    try:
        current_cart = get_or_create_cart(request)
        return {"cart": current_cart, "cart_count": current_cart.total_quantity}
    except Exception:
        return {"cart": None, "cart_count": 0}
