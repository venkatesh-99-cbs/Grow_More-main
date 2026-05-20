from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from products.models import Category, Product


def product_payload(product):
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "category": product.category.slug,
        "categoryName": product.category.name,
        "price": float(product.current_price),
        "originalPrice": float(product.original_price),
        "discountPercent": product.discount_percent,
        "offer": {
            "label": product.offer_label,
            "highlight": product.offer_highlight,
            "endsAt": product.offer_countdown_target,
        } if product.active_offer else None,
        "desc": product.description,
        "sizes": product.sizes,
        "colors": product.colors,
        "stock": product.stock,
        "isTrending": product.is_trending,
        "isFeatured": product.is_featured,
        "url": product.get_absolute_url(),
        "images": product.gallery_images,
    }


@ensure_csrf_cookie
def shop(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.filter(is_active=True)
    return render(request, "products/shop.html", {"products": products, "categories": categories})


@ensure_csrf_cookie
def detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk).select_related("category")[:3]
    return render(request, "products/detail.html", {"product": product, "related": related})


@ensure_csrf_cookie
def favorites(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    return render(request, "products/favorites.html", {"products": products})


def product_api(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "featured")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    if category and category != "all":
        products = products.filter(category__slug=category)
    if sort == "price-low":
        products = sorted(products, key=lambda p: p.current_price)
    elif sort == "price-high":
        products = sorted(products, key=lambda p: p.current_price, reverse=True)
    elif sort == "name":
        products = products.order_by("name")
    return JsonResponse({"products": [product_payload(product) for product in products]})

# Create your views here.
