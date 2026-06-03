from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_branded_email(subject, template_name, context, recipient_list, attachments=None):
    """Utility to send branded HTML emails with a plain text fallback."""
    context['site_url'] = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://localhost:8000'
    if not context['site_url'].startswith('http'):
        # For local dev, use http
        if 'localhost' in context['site_url'] or '127.0.0.1' in context['site_url']:
             context['site_url'] = 'http://' + context['site_url']
        else:
            context['site_url'] = 'https://' + context['site_url']

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list
    )
    email.attach_alternative(html_content, "text/html")

    if attachments:
        for attachment in attachments:
            email.attach(*attachment)

    return email.send(fail_silently=True)

def send_welcome_email(user):
    return send_branded_email(
        "Welcome to Grow More!",
        "emails/welcome.html",
        {"user": user},
        [user.email]
    )

def send_order_confirmation(order):
    from orders.services import generate_order_invoice_pdf

    attachments = []
    pdf_buffer = generate_order_invoice_pdf(order)
    if pdf_buffer:
        attachments.append((
            f"Payment_Receipt_{order.order_number}.pdf",
            pdf_buffer.getvalue(),
            "application/pdf"
        ))

    return send_branded_email(
        f"Order Confirmation - #{order.order_number}",
        "emails/order_confirmation.html",
        {"order": order},
        [order.user.email],
        attachments=attachments
    )