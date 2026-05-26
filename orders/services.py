import hashlib
import hmac
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.db import transaction

from orders.models import Cart, CartItem, Order, OrderItem, Payment

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


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


def _brand_logo_path():
    logo_path = settings.BASE_DIR / "media" / "products" / "main" / "Grow_More_logo.png"
    return logo_path if logo_path.exists() else None


def _payment_status(order):
    payment = getattr(order, "payment", None)
    return payment.get_status_display() if payment else "Not recorded"


def _brand_header(styles, title, subtitle):
    title_style = ParagraphStyle(
        name=f"{title}Title",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=4,
        alignment=2,
        fontName="Helvetica-Bold",
    )
    brand_block = [
        Paragraph("<b>GROW MORE</b>", styles["Heading2"]),
        Paragraph("Premium Summer Menswear", styles["Normal"]),
    ]
    logo_path = _brand_logo_path()
    if logo_path:
        brand_block.insert(0, Image(str(logo_path), width=0.7 * inch, height=0.7 * inch, kind="proportional"))

    header = Table(
        [[brand_block, [Paragraph(title, title_style), Paragraph(subtitle, styles["Normal"])]]],
        colWidths=[3.2 * inch, 3.3 * inch],
    )
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return header


def generate_order_invoice_pdf(order):
    """
    Generate a professional payment receipt PDF.
    Kept under the original function name so older invoice URLs remain compatible.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story = []
    styles = getSampleStyleSheet()

    story.append(_brand_header(styles, "PAYMENT RECEIPT", f"Receipt #{order.order_number}"))
    story.append(Spacer(1, 0.12 * inch))

    receipt_data = [
        [Paragraph("<b>Order Number</b>", styles["Normal"]), Paragraph(order.order_number, styles["Normal"])],
        [Paragraph("<b>Receipt Date</b>", styles["Normal"]), Paragraph(order.created_at.strftime("%d-%b-%Y"), styles["Normal"])],
        [Paragraph("<b>Payment Method</b>", styles["Normal"]), Paragraph(order.get_payment_method_display(), styles["Normal"])],
        [Paragraph("<b>Payment Status</b>", styles["Normal"]), Paragraph(_payment_status(order), styles["Normal"])],
    ]
    receipt_table = Table(receipt_data, colWidths=[1.6 * inch, 4.8 * inch])
    receipt_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f6fbfb")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(receipt_table)
    story.append(Spacer(1, 0.15 * inch))

    customer_data = [
        [Paragraph("<b>Customer</b>", styles["Heading3"]), Paragraph("<b>Shipping Address</b>", styles["Heading3"])],
        [
            Paragraph(f"{order.full_name}<br/>{order.email}<br/>{order.phone}", styles["Normal"]),
            Paragraph(f"{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state}<br/>{order.shipping_postal_code}", styles["Normal"]),
        ],
    ]
    customer_table = Table(customer_data, colWidths=[3.2 * inch, 3.2 * inch])
    customer_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#eeeeee")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(customer_table)
    story.append(Spacer(1, 0.15 * inch))

    items_data = [
        [
            Paragraph("<b>Product</b>", styles["Normal"]),
            Paragraph("<b>Size</b>", styles["Normal"]),
            Paragraph("<b>Qty</b>", styles["Normal"]),
            Paragraph("<b>Paid Price</b>", styles["Normal"]),
            Paragraph("<b>Total</b>", styles["Normal"]),
        ]
    ]
    for item in order.items.all():
        items_data.append(
            [
                Paragraph(item.product_name, styles["Normal"]),
                Paragraph(item.size or "-", styles["Normal"]),
                Paragraph(str(item.quantity), styles["Normal"]),
                Paragraph(f"Rs. {item.price:.2f}", styles["Normal"]),
                Paragraph(f"Rs. {item.subtotal:.2f}", styles["Normal"]),
            ]
        )

    items_table = Table(items_data, colWidths=[2.45 * inch, 0.7 * inch, 0.65 * inch, 1.1 * inch, 1.15 * inch])
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#20343a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d6d6d6")),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.15 * inch))

    totals_data = [
        [Paragraph("<b>Subtotal</b>", styles["Normal"]), Paragraph(f"Rs. {order.total_amount:.2f}", styles["Normal"])],
        [Paragraph("<b>Shipping</b>", styles["Normal"]), Paragraph("Free", styles["Normal"])],
        [Paragraph("<b>Amount Paid</b>", styles["Heading3"]), Paragraph(f"<b>Rs. {order.total_amount:.2f}</b>", styles["Heading3"])],
    ]
    totals_table = Table(totals_data, colWidths=[4.7 * inch, 1.5 * inch], hAlign="RIGHT")
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f6fbfb")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(totals_table)
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph("This receipt confirms payment recorded for the order above.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_delivery_sheet_pdf(order):
    """
    Generate a shipping sheet PDF for dispatch and packing.
    Kept under the original function name so older delivery-sheet URLs remain compatible.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story = []
    styles = getSampleStyleSheet()

    story.append(_brand_header(styles, "SHIPPING SHEET", f"Ship order #{order.order_number}"))
    story.append(Spacer(1, 0.14 * inch))

    details_data = [
        [Paragraph("<b>Order Number</b>", styles["Normal"]), Paragraph(order.order_number, styles["Normal"])],
        [Paragraph("<b>Order Date</b>", styles["Normal"]), Paragraph(order.created_at.strftime("%d-%b-%Y"), styles["Normal"])],
        [Paragraph("<b>Order Status</b>", styles["Normal"]), Paragraph(order.get_status_display(), styles["Normal"])],
        [Paragraph("<b>Payment</b>", styles["Normal"]), Paragraph(f"{order.get_payment_method_display()} - {_payment_status(order)}", styles["Normal"])],
    ]
    details_table = Table(details_data, colWidths=[1.6 * inch, 4.7 * inch])
    details_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f6fbfb")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(details_table)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("<b>SHIP TO</b>", styles["Heading3"]))
    addr_text = f"{order.full_name}<br/>{order.phone}<br/>{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}"
    story.append(Paragraph(addr_text, styles["Normal"]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("<b>PACKING CHECKLIST</b>", styles["Heading3"]))
    items_data = [
        [
            Paragraph("<b>Product</b>", styles["Normal"]),
            Paragraph("<b>Size</b>", styles["Normal"]),
            Paragraph("<b>Color</b>", styles["Normal"]),
            Paragraph("<b>Qty</b>", styles["Normal"]),
            Paragraph("<b>Checked</b>", styles["Normal"]),
        ],
    ]
    for item in order.items.all():
        items_data.append(
            [
                Paragraph(item.product_name, styles["Normal"]),
                Paragraph(item.size or "-", styles["Normal"]),
                Paragraph(item.color or "-", styles["Normal"]),
                Paragraph(str(item.quantity), styles["Normal"]),
                Paragraph("[  ]", styles["Normal"]),
            ]
        )

    items_table = Table(items_data, colWidths=[2.7 * inch, 0.75 * inch, 1.15 * inch, 0.65 * inch, 0.8 * inch])
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#20343a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#222222")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 0.2 * inch))

    handoff_data = [
        [Paragraph("<b>Packed By</b>", styles["Normal"]), Paragraph("____________________", styles["Normal"])],
        [Paragraph("<b>Dispatch Partner</b>", styles["Normal"]), Paragraph("____________________", styles["Normal"])],
        [Paragraph("<b>Tracking Number</b>", styles["Normal"]), Paragraph("____________________", styles["Normal"])],
    ]
    handoff_table = Table(handoff_data, colWidths=[1.7 * inch, 4.4 * inch])
    handoff_table.setStyle(TableStyle([("PADDING", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd"))]))
    story.append(handoff_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Verify product, size, color, and quantity before sealing the package.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer
