import hashlib
import hmac
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from orders.models import Cart, CartItem, Order, OrderItem, Payment


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


def merge_session_cart_into_user(request):
    if not request.user.is_authenticated or not request.session.session_key:
        return
    session_cart = Cart.objects.filter(session_key=request.session.session_key, user=None).first()
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    if not session_cart:
        return
    for item in session_cart.items.select_related("product"):
        existing, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            size=item.size,
            color=item.color,
            defaults={"quantity": item.quantity},
        )
        if not created:
            existing.quantity += item.quantity
            existing.save(update_fields=["quantity"])
    session_cart.delete()


@transaction.atomic
def create_order_from_cart(cart, user, form_data):
    items = list(cart.items.select_related("product"))
    if not items:
        raise ValueError("Cart is empty.")
    order = Order.objects.create(
        user=user if user and user.is_authenticated else None,
        email=form_data["email"],
        phone=form_data["phone"],
        full_name=form_data["full_name"],
        shipping_address=form_data["shipping_address"],
        shipping_city=form_data["shipping_city"],
        shipping_state=form_data["shipping_state"],
        shipping_postal_code=form_data["shipping_postal_code"],
        payment_method=form_data.get("payment_method", "razorpay"),
    )
    total = Decimal("0.00")
    for cart_item in items:
        product = cart_item.product
        active_offer = product.active_offer
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            size=cart_item.size,
            color=cart_item.color,
            quantity=cart_item.quantity,
            price=product.current_price,
            original_price=product.price,
            offer_title=active_offer.title if active_offer else "",
            offer_discount_percent=active_offer.discount_percent if active_offer else 0,
        )
        total += product.current_price * cart_item.quantity
        if product.stock >= cart_item.quantity:
            product.stock -= cart_item.quantity
            product.save(update_fields=["stock"])
    order.total_amount = total
    order.save(update_fields=["total_amount"])
    return order


def create_payment_record(order):
    provider_order_id = ""
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            import razorpay

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            amount_paise = int(order.total_amount * 100)
            provider_order = client.order.create(
                {
                    "amount": amount_paise,
                    "currency": settings.RAZORPAY_CURRENCY,
                    "receipt": order.order_number,
                    "payment_capture": 1,
                }
            )
            provider_order_id = provider_order.get("id", "")
        except Exception:
            provider_order_id = ""
    return Payment.objects.create(order=order, provider_order_id=provider_order_id)


def verify_razorpay_signature(provider_order_id, provider_payment_id, signature):
    if not settings.RAZORPAY_KEY_SECRET:
        return False
    message = f"{provider_order_id}|{provider_payment_id}".encode()
    expected = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
