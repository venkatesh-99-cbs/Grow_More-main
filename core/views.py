from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from core.forms import ContactForm
from core.models import HeroBanner, HomepageSection
from products.models import Product


@ensure_csrf_cookie
def home(request):
    banners = HeroBanner.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related("category")[:4]
    deal_products = [product for product in Product.objects.filter(is_active=True).select_related("category") if product.active_offer][:6]
    sections = HomepageSection.objects.filter(is_active=True)
    return render(request, "core/home.html", {"banners": banners, "featured_products": featured_products, "deal_products": deal_products, "sections": sections})


@ensure_csrf_cookie
def about(request):
    return render(request, "core/about.html")



@ensure_csrf_cookie
def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        send_mail(
            f"Grow More contact from {form.cleaned_data['name']}",
            form.cleaned_data["message"],
            form.cleaned_data["email"],
            ["hello@growmore.com"],
            fail_silently=True,
        )
        messages.success(request, "Thanks, we will contact you soon.")
        return redirect("core:contact")
    return render(request, "core/contact.html", {"form": form})
