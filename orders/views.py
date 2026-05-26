import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from orders.forms import CheckoutForm
from orders.models import CartItem, Order, Payment
from orders.services import create_order_from_cart, create_payment_record, get_or_create_cart, verify_razorpay_signature
from products.models import Product


def cart_payload(cart):
    items = []
    for item in cart.items.select_related("product", "product__category"):
        product = item.product
        items.append(
            {
                "id": item.id,
                "productId": product.id,
                "name": product.name,
                "url": product.get_absolute_url(),
                "price": float(product.current_price),
                "originalPrice": float(product.original_price),
                "offerLabel": product.offer_label if product.active_offer else "",
                "qty": item.quantity,
                "size": item.size,
                "color": item.color,
                "image": product.main_image_url,
                "subtotal": float(item.subtotal),
            }
        )
    return {"items": items, "total": float(cart.total), "count": cart.total_quantity}


def cart_api(request):
    cart = get_or_create_cart(request)
    return JsonResponse(cart_payload(cart))


@require_POST
def add_to_cart(request):
    cart = get_or_create_cart(request)
    data = json.loads(request.body.decode("utf-8") or "{}") if request.body else request.POST
    product = get_object_or_404(Product, pk=data.get("product_id"), is_active=True)
    quantity = max(1, int(data.get("quantity", 1)))
    size = str(data.get("size", product.sizes[0] if product.sizes else "")).strip()
    color = str(data.get("color", product.colors[0] if product.colors else "")).strip()
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        color=color,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity
        item.save(update_fields=["quantity"])
    return JsonResponse(cart_payload(cart))


@require_POST
def update_cart_item(request, pk):
    cart = get_or_create_cart(request)
    data = json.loads(request.body.decode("utf-8") or "{}") if request.body else request.POST
    item = get_object_or_404(CartItem, pk=pk, cart=cart)
    quantity = int(data.get("quantity", item.quantity))
    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, 99)
        item.save(update_fields=["quantity"])
    return JsonResponse(cart_payload(cart))


@require_POST
def remove_cart_item(request, pk):
    cart = get_or_create_cart(request)
    get_object_or_404(CartItem, pk=pk, cart=cart).delete()
    return JsonResponse(cart_payload(cart))


@ensure_csrf_cookie
@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("products:shop")
    initial = {"email": request.user.email, "full_name": request.user.get_full_name() or request.user.username}
    default_address = request.user.addresses.filter(is_default=True).first()
    if default_address:
        initial.update(
            {
                "full_name": default_address.full_name,
                "phone": default_address.phone,
                "shipping_address": default_address.address_line,
                "shipping_city": default_address.city,
                "shipping_state": default_address.state,
                "shipping_postal_code": default_address.postal_code,
            }
        )
    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            order = create_order_from_cart(cart, request.user, form.cleaned_data)
        except ValueError:
            messages.error(request, "Your cart is empty.")
            return redirect("products:shop")
        payment = create_payment_record(order)
        if order.payment_method == "cod":
            order.status = "confirmed"
            order.save(update_fields=["status"])
            payment.status = "paid"
            payment.save(update_fields=["status"])
            cart.items.all().delete()
            return redirect("orders:success", order_number=order.order_number)
        return render(request, "orders/payment.html", {"order": order, "payment": payment, "razorpay_key_id": settings.RAZORPAY_KEY_ID})
    return render(request, "orders/checkout.html", {"form": form, "cart": cart})


@require_POST
@login_required
def verify_payment(request):
    provider_order_id = request.POST.get("razorpay_order_id", "")
    provider_payment_id = request.POST.get("razorpay_payment_id", "")
    signature = request.POST.get("razorpay_signature", "")
    payment = get_object_or_404(Payment, provider_order_id=provider_order_id, order__user=request.user)
    if verify_razorpay_signature(provider_order_id, provider_payment_id, signature):
        payment.provider_payment_id = provider_payment_id
        payment.provider_signature = signature
        payment.status = "paid"
        payment.raw_response = dict(request.POST.items())
        payment.save()
        payment.order.status = "confirmed"
        payment.order.save(update_fields=["status"])
        get_or_create_cart(request).items.all().delete()
        return redirect("orders:success", order_number=payment.order.order_number)
    payment.status = "failed"
    payment.raw_response = dict(request.POST.items())
    payment.save()
    messages.error(request, "Payment verification failed. Please contact support if money was debited.")
    return redirect("orders:checkout")


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    return render(request, "orders/success.html", {"order": order})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    return render(request, "orders/detail.html", {"order": order})


@login_required
def download_payment_receipt(request, order_number):
    """Download order payment receipt as PDF."""
    from orders.services import generate_order_invoice_pdf
    from django.http import FileResponse

    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    pdf_buffer = generate_order_invoice_pdf(order)

    if pdf_buffer is None:
        messages.error(request, "PDF generation is not available. Please contact support.")
        return redirect("orders:detail", order_number=order_number)

    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment-receipt-{order.order_number}.pdf"'
    return response


@login_required  
def download_shipping_sheet(request, order_number):
    """Download order shipping sheet as PDF."""
    from orders.services import generate_delivery_sheet_pdf
    from django.http import FileResponse

    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    pdf_buffer = generate_delivery_sheet_pdf(order)

    if pdf_buffer is None:
        messages.error(request, "PDF generation is not available. Please contact support.")
        return redirect("orders:detail", order_number=order_number)

    response = FileResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipping-sheet-{order.order_number}.pdf"'
    return response


download_invoice = download_payment_receipt
download_delivery_sheet = download_shipping_sheet

# Create your views here.
