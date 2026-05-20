from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.forms import HeroBannerForm, HomepageSectionForm
from core.models import HeroBanner, HomepageSection
from offers.forms import PromotionalOfferForm
from offers.models import PromotionalOffer
from orders.models import Order, Payment
from products.forms import CategoryForm, ProductForm
from products.models import Category, Product


@staff_member_required
def overview(request):
    stats = {
        "products": Product.objects.count(),
        "offers": PromotionalOffer.objects.filter(is_active=True).count(),
        "orders": Order.objects.count(),
        "customers": User.objects.filter(is_staff=False).count(),
        "revenue": Order.objects.filter(payment__status="paid").aggregate(total=Sum("total_amount"))["total"] or 0,
    }
    orders = Order.objects.select_related("user").prefetch_related("items")[:8]
    return render(request, "dashboard/overview.html", {"stats": stats, "orders": orders})


@staff_member_required
def products(request):
    items = Product.objects.select_related("category").all()
    return render(request, "dashboard/products.html", {"products": items})


@staff_member_required
def product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product saved.")
        return redirect("dashboard:products")
    return render(request, "dashboard/product_form.html", {"form": form, "product": product})


@staff_member_required
def categories(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category saved.")
        return redirect("dashboard:categories")
    return render(request, "dashboard/categories.html", {"form": form, "categories": Category.objects.all()})


@staff_member_required
def homepage(request):
    banner_form = HeroBannerForm()
    section_form = HomepageSectionForm()
    return render(
        request,
        "dashboard/homepage.html",
        {"banner_form": banner_form, "section_form": section_form, "banners": HeroBanner.objects.all(), "sections": HomepageSection.objects.all()},
    )


@staff_member_required
@require_POST
def banner_create(request):
    form = HeroBannerForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        messages.success(request, "Hero banner saved.")
    else:
        messages.error(request, "Please check hero banner details.")
    return redirect("dashboard:homepage")


@staff_member_required
@require_POST
def banner_delete(request, pk):
    get_object_or_404(HeroBanner, pk=pk).delete()
    messages.success(request, "Hero banner removed.")
    return redirect("dashboard:homepage")


@staff_member_required
@require_POST
def section_create(request):
    form = HomepageSectionForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Homepage section saved.")
    return redirect("dashboard:homepage")


@staff_member_required
def orders(request):
    items = Order.objects.select_related("user").prefetch_related("items", "payment").all()
    return render(request, "dashboard/orders.html", {"orders": items, "status_choices": Order.STATUS_CHOICES})


@staff_member_required
@require_POST
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status")
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save(update_fields=["status"])
        messages.success(request, "Order status updated.")
    return redirect("dashboard:orders")


@staff_member_required
def customers(request):
    users = User.objects.filter(is_staff=False).prefetch_related("orders", "addresses")
    return render(request, "dashboard/customers.html", {"customers": users})


@staff_member_required
def payments(request):
    return render(request, "dashboard/payments.html", {"payments": Payment.objects.select_related("order").all()})


@staff_member_required
def offers(request):
    items = PromotionalOffer.objects.prefetch_related("products", "categories").all()
    return render(request, "dashboard/offers.html", {"offers": items})


@staff_member_required
def offer_form(request, pk=None):
    offer = get_object_or_404(PromotionalOffer, pk=pk) if pk else None
    form = PromotionalOfferForm(request.POST or None, request.FILES or None, instance=offer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Promotional offer saved.")
        return redirect("dashboard:offers")
    return render(request, "dashboard/offer_form.html", {"form": form, "offer": offer})


@staff_member_required
@require_POST
def offer_delete(request, pk):
    get_object_or_404(PromotionalOffer, pk=pk).delete()
    messages.success(request, "Promotional offer removed.")
    return redirect("dashboard:offers")

# Create your views here.
