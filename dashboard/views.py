from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count, ProtectedError
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.forms import HeroBannerForm, HeroGroupForm
from core.models import HeroBanner, HeroGroup
from offers.forms import PromotionalOfferForm
from offers.models import PromotionalOffer
from orders.models import Order, Payment
from products.forms import BrandForm, CategoryForm, ProductForm
from products.cloudinary_utils import delete_product_image
from products.models import Brand, Category, Product


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
        try:
            form.save()
            messages.success(request, "Product saved.")
            return redirect("dashboard:products")
        except ValidationError as exc:
            form.add_error(None, exc)
            messages.error(request, "Please check the product image and try again.")
    return render(request, "dashboard/product_form.html", {"form": form, "product": product})


@staff_member_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    try:
        public_id = product.cloudinary_public_id
        product.delete()
        delete_product_image(public_id)
        messages.success(request, f"{name} removed.")
    except ProtectedError:
        product.is_active = False
        product.save(update_fields=["is_active"])
        messages.warning(request, f"{name} has order history, so it was hidden from the storefront instead.")
    return redirect("dashboard:products")


@staff_member_required
def categories(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else None
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Category saved.")
        return redirect("dashboard:categories")
    categories_qs = Category.objects.annotate(product_count=Count("products"))
    return render(
        request,
        "dashboard/categories.html",
        {"form": form, "categories": categories_qs, "category": category},
    )


@staff_member_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    try:
        category.delete()
        messages.success(request, f"{name} removed.")
    except ProtectedError:
        category.is_active = False
        category.save(update_fields=["is_active"])
        messages.warning(request, f"{name} is used by products, so it was hidden instead.")
    return redirect("dashboard:categories")


@staff_member_required
def brands(request, pk=None):
    brand = get_object_or_404(Brand, pk=pk) if pk else None
    form = BrandForm(request.POST or None, instance=brand)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Brand saved.")
        return redirect("dashboard:brands")
    brands_qs = Brand.objects.annotate(product_count=Count("products"))
    return render(
        request,
        "dashboard/brands.html",
        {"form": form, "brands": brands_qs, "brand": brand},
    )


@staff_member_required
@require_POST
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    name = brand.name
    try:
        brand.delete()
        messages.success(request, f"{name} removed.")
    except ProtectedError:
        brand.is_active = False
        brand.save(update_fields=["is_active"])
        messages.warning(request, f"{name} is used by products, so it was hidden instead.")
    return redirect("dashboard:brands")


@staff_member_required
def homepage(request, pk=None):
    group = get_object_or_404(HeroGroup, pk=pk) if pk else None
    group_form = HeroGroupForm(request.POST or None, instance=group)
    if request.method == "POST" and "save_group" in request.POST:
        if group_form.is_valid():
            group_form.save()
            messages.success(request, "Hero group saved.")
            return redirect("dashboard:homepage")

    banner_form = HeroBannerForm()
    return render(
        request,
        "dashboard/homepage.html",
        {
            "banner_form": banner_form,
            "group_form": group_form,
            "banners": HeroBanner.objects.select_related("group").all(),
            "groups": HeroGroup.objects.all(),
            "current_group": group
        },
    )


@staff_member_required
@require_POST
def group_delete(request, pk):
    get_object_or_404(HeroGroup, pk=pk).delete()
    messages.success(request, "Hero group removed.")
    return redirect("dashboard:homepage")


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
    users = User.objects.filter(is_staff=False).prefetch_related("orders__items", "addresses")
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


@staff_member_required
def admin_download_payment_receipt(request, pk):
    """Admin endpoint to download order payment receipt as PDF."""
    from django.http import FileResponse
    from orders.services import generate_order_invoice_pdf

    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    pdf_buffer = generate_order_invoice_pdf(order)

    if pdf_buffer is None:
        messages.error(request, "PDF generation is not available.")
        return redirect("dashboard:orders")

    response = FileResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="payment-receipt-{order.order_number}.pdf"'
    return response


@staff_member_required
def admin_download_shipping_sheet(request, pk):
    """Admin endpoint to download order shipping sheet as PDF."""
    from django.http import FileResponse
    from orders.services import generate_delivery_sheet_pdf

    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk)
    pdf_buffer = generate_delivery_sheet_pdf(order)

    if pdf_buffer is None:
        messages.error(request, "PDF generation is not available.")
        return redirect("dashboard:orders")

    response = FileResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="shipping-sheet-{order.order_number}.pdf"'
    return response


admin_download_invoice = admin_download_payment_receipt
admin_download_delivery_sheet = admin_download_shipping_sheet
