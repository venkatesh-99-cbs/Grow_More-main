from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from core.forms import ContactForm
from core.models import HeroBanner, HomepageSection
from products.models import Product


@ensure_csrf_cookie
def home(request):
    from offers.services import active_offers

    if request.GET.get("lazy") == "deals":
        deal_products = [product for product in Product.objects.filter(is_active=True).select_related("category") if product.active_offer][:6]
        return render(request, "partials/product_grid.html", {"products": deal_products})

    banners = HeroBanner.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:4]
    sections = HomepageSection.objects.filter(is_active=True)
    current_offers = active_offers()

    return render(request, "core/home.html", {
        "banners": banners,
        "featured_products": featured_products,
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
<<<<<<< HEAD
        try:
            send_mail(
                f"Grow More contact from {form.cleaned_data['name']}",
                f"Message from {form.cleaned_data['name']} ({form.cleaned_data['email']}):\n\n{form.cleaned_data['message']}",
                form.cleaned_data["email"],
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Thanks, we will contact you soon.")
        except Exception:
            messages.error(request, "Sorry, there was an error sending your message. Please try again later.")

=======
        send_mail(
            f"Grow More contact from {form.cleaned_data['name']}",
            form.cleaned_data["message"],
            form.cleaned_data["email"],
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        messages.success(request, "Thanks, we will contact you soon.")
>>>>>>> origin/main
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})
