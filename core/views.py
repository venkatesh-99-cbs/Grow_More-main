from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from core.forms import ContactForm
from core.models import HeroBanner, HomepageSection
from products.models import Product


@ensure_csrf_cookie
def home(request):
    from offers.services import active_offers, get_products_with_active_offers

    if request.GET.get("lazy") == "deals":
        deal_products = get_products_with_active_offers(limit=6)
        if not deal_products.exists():
            deal_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:6]
        return render(request, "partials/product_grid.html", {"products": deal_products})

    banners = HeroBanner.objects.filter(is_active=True).select_related('group')
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:4]

    fallback_products = []
    if not featured_products:
        # Fallback to products with offers, then any active products
        fallback_products = get_products_with_active_offers(limit=4)
        if not fallback_products:
            fallback_products = Product.objects.filter(is_active=True).select_related("category")[:4]

    sections = HomepageSection.objects.filter(is_active=True)
    current_offers = active_offers()

    return render(request, "core/home.html", {
        "banners": banners,
        "featured_products": featured_products,
        "fallback_products": fallback_products,
        "sections": sections,
        "active_offers": current_offers
    })


@ensure_csrf_cookie
def about(request):
    return render(request, "core/about.html")



@ensure_csrf_cookie
def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        name    = form.cleaned_data["name"]
        email   = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        email_body = (
            f"You have a new message from the Grow More contact form.\n"
            f"{'=' * 52}\n\n"
            f"Customer Name  : {name}\n"
            f"Customer Email : {email}\n\n"
            f"Message\n"
            f"{'-' * 52}\n"
            f"{message}\n\n"
            f"{'=' * 52}\n"
            f"Reply directly to this email to respond to {name}.\n"
        )

        EmailMessage(
            subject=f"[Grow More] New message from {name} <{email}>",
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[email],
        ).send(fail_silently=False)
        messages.success(request, "Thanks, we will contact you soon.")
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})
