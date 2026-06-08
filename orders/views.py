import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from core.services import send_order_confirmation
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
    size = str(data.get("size", data.get("size", ""))).strip()
    color_val = str(data.get("color", data.get("color", "")) or product.safe_color_hex).strip()

    # If color_val is a hex code matching the product, use color_name if available
    if color_val.lower() == product.safe_color_hex.lower() and product.color_name:
        color = product.color_name
    else:
        color = color_val

    # Validate size selection if product has sizes
    if product.sizes and not size:
        return JsonResponse({"success": False, "error": "Please select a size"}, status=400)

    # Check stock for the specific size
    if size:
        from products.models import SizeStock
        size_stock = SizeStock.objects.filter(product=product, size=size).first()
        if size_stock:
            available = size_stock.available_quantity
            # Check existing items in cart for same product/size
            existing_in_cart = CartItem.objects.filter(cart=cart, product=product, size=size).first()
            requested_total = quantity + (existing_in_cart.quantity if existing_in_cart else 0)

            if available < requested_total:
                return JsonResponse({
                    "success": False,
                    "error": f"Only {available} items available for size {size}"
                }, status=400)
    elif product.stock < quantity:
         return JsonResponse({"success": False, "error": "Insufficient stock"}, status=400)

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
            send_order_confirmation(order)
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
        send_order_confirmation(payment.order)
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

    # Security: Only allow for SUCCESSFUL status (confirmed/delivered/shipped)
    # The requirement said "SUCCESSFUL", which usually means paid or confirmed.
    # Block access for: Pending, Failed, Cancelled
    if order.status in ['pending', 'failed', 'cancelled']:
        messages.error(request, f"Receipt download is not available for orders with status: {order.status.upper()}.")
        return redirect("orders:detail", order_number=order_number)

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
    if not request.user.is_staff:
        messages.error(request, "Access denied. Only staff can access shipping sheets.")
        return redirect("orders:detail", order_number=order_number)

    from orders.services import generate_delivery_sheet_pdf
    from django.http import FileResponse

    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number)
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
