import hashlib
import hmac
from decimal import Decimal
from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.db import transaction

from orders.models import Cart, CartItem, Order, OrderItem, Payment

# PDF Generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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


# ============================================================================
# Invoice PDF Generation
# ============================================================================


def generate_order_invoice_pdf(order):
    """
    Generate a professional order invoice PDF.
    Returns BytesIO buffer with PDF content, or None if reportlab not available.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story = []
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )

    # Header
    story.append(Paragraph("GROW MORE", title_style))
    story.append(Paragraph("Premium Summer Fashion Store", styles['Normal']))
    story.append(Spacer(1, 0.15 * inch))

    # Invoice header
    header_data = [
        [Paragraph(f"<b>Invoice #{order.order_number}</b>", styles['Heading2']), 
         Paragraph(f"<b>Date:</b> {order.created_at.strftime('%d-%b-%Y')}", styles['Normal'])],
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 2.5 * inch])
    header_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
    story.append(header_table)
    story.append(Spacer(1, 0.15 * inch))

    # Customer info
    cust_data = [
        [Paragraph("<b>BILL TO:</b>", styles['Heading3']), Paragraph("<b>SHIP TO:</b>", styles['Heading3'])],
        [
            Paragraph(
                f"{order.full_name}<br/>{order.email}<br/>{order.phone}",
                styles['Normal']
            ),
            Paragraph(
                f"{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state}<br/>{order.shipping_postal_code}",
                styles['Normal']
            ),
        ],
    ]
    cust_table = Table(cust_data, colWidths=[3.25 * inch, 3.25 * inch])
    cust_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.append(cust_table)
    story.append(Spacer(1, 0.15 * inch))

    # Items table
    items_data = [
        [
            Paragraph("<b>Product</b>", styles['Normal']),
            Paragraph("<b>Size</b>", styles['Normal']),
            Paragraph("<b>Qty</b>", styles['Normal']),
            Paragraph("<b>Price</b>", styles['Normal']),
            Paragraph("<b>Total</b>", styles['Normal']),
        ]
    ]

    for item in order.items.all():
        items_data.append(
            [
                Paragraph(item.product_name, styles['Normal']),
                Paragraph(item.size or '-', styles['Normal']),
                Paragraph(str(item.quantity), styles['Normal']),
                Paragraph(f"₹{item.price:.2f}", styles['Normal']),
                Paragraph(f"₹{item.price * item.quantity:.2f}", styles['Normal']),
            ]
        )

    items_table = Table(items_data, colWidths=[2.5 * inch, 0.7 * inch, 0.7 * inch, 1 * inch, 1.1 * inch])
    items_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 0.15 * inch))

    # Totals
    totals_data = [
        [Paragraph("<b>Subtotal:</b>", styles['Normal']), Paragraph(f"₹{order.total_amount:.2f}", styles['Normal'])],
        [Paragraph("<b>Shipping:</b>", styles['Normal']), Paragraph("Free", styles['Normal'])],
        [Paragraph("<b>TOTAL:</b>", styles['Heading3']), Paragraph(f"<b>₹{order.total_amount:.2f}</b>", styles['Heading3'])],
    ]
    totals_table = Table(totals_data, colWidths=[4.5 * inch, 1.5 * inch])
    totals_table.setStyle(
        TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, -2), (-1, -1), 1, colors.HexColor('#999999')),
        ])
    )
    story.append(totals_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_delivery_sheet_pdf(order):
    """
    Generate a delivery sheet (packing sheet) PDF.
    Returns BytesIO buffer with PDF content, or None if reportlab not available.
    """
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        name='DeliveryTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    story.append(Paragraph("DELIVERY SHEET", title_style))
    story.append(Spacer(1, 0.1 * inch))

    # Order details
    details_data = [
        [Paragraph("<b>Order #:</b>", styles['Normal']), Paragraph(order.order_number, styles['Normal'])],
        [Paragraph("<b>Date:</b>", styles['Normal']), Paragraph(order.created_at.strftime('%d-%b-%Y'), styles['Normal'])],
        [Paragraph("<b>Status:</b>", styles['Normal']), Paragraph(order.get_status_display(), styles['Normal'])],
    ]
    details_table = Table(details_data, colWidths=[1.5 * inch, 4.5 * inch])
    details_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
    story.append(details_table)
    story.append(Spacer(1, 0.15 * inch))

    # Delivery address
    story.append(Paragraph("<b>DELIVER TO:</b>", styles['Heading3']))
    addr_text = f"{order.full_name}<br/>{order.phone}<br/>{order.shipping_address}<br/>{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}"
    story.append(Paragraph(addr_text, styles['Normal']))
    story.append(Spacer(1, 0.15 * inch))

    # Items
    story.append(Paragraph("<b>ITEMS TO PACK:</b>", styles['Heading3']))

    items_data = [
        [Paragraph("<b>Product</b>", styles['Normal']), Paragraph("<b>Size</b>", styles['Normal']), Paragraph("<b>Qty</b>", styles['Normal'])],
    ]
    for item in order.items.all():
        items_data.append(
            [
                Paragraph(item.product_name, styles['Normal']),
                Paragraph(item.size or '-', styles['Normal']),
                Paragraph(str(item.quantity), styles['Normal']),
            ]
        )

    items_table = Table(items_data, colWidths=[3.5 * inch, 1 * inch, 1 * inch])
    items_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
    )
    story.append(items_table)
    story.append(Spacer(1, 0.2 * inch))

    # Notes
    story.append(Paragraph("<b>NOTES:</b>", styles['Heading3']))
    story.append(Paragraph("Please verify all items and quantities before handing to customer.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

