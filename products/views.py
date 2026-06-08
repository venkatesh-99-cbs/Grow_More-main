import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Min
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from products.models import Category, Product, Brand, SizeStock, Wishlist


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
        "colors": product.get_colors_display(),
        "color_hex": product.safe_color_hex,
        "stock": product.stock,
        "isTrending": product.is_trending,
        "isFeatured": product.is_featured,
        "url": product.get_absolute_url(),
        "images": product.gallery_images,
    }


@ensure_csrf_cookie
def shop(request):
    products = Product.objects.filter(is_active=True).select_related("category", "brand")

    # Apply filters
    q = request.GET.get("q", "").strip()
    categories_filter = request.GET.getlist("category")
    brands_filter = request.GET.getlist("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sizes_filter = request.GET.getlist("size")
    sort = request.GET.get("sort", "featured")

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if categories_filter and "all" not in categories_filter:
        products = products.filter(category__slug__in=categories_filter)

    if brands_filter:
        products = products.filter(brand__slug__in=brands_filter)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sizes_filter:
        products = products.filter(size_stocks__size__in=sizes_filter, size_stocks__stock_quantity__gt=0).distinct()

    # Sorting
    if sort == "price-low":
        products = products.order_by("price")
    elif sort == "price-high":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")
    else:
        products = products.order_by("-is_featured", "-is_trending", "name")

    if request.GET.get("partial") == "true":
        return render(request, "partials/product_grid.html", {"products": products})

    categories = Category.objects.filter(is_active=True)
    brands = Brand.objects.filter(is_active=True)
    size_choices = SizeStock.SIZE_CHOICES

    return render(request, "products/shop.html", {
        "products": products,
        "categories": categories,
        "brands": brands,
        "size_choices": size_choices
    })


@ensure_csrf_cookie
def detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)

    if request.GET.get("lazy") == "true":
        related = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk).select_related("category")[:3]
        return render(request, "partials/product_grid.html", {"products": related})

    return render(request, "products/detail.html", {"product": product})


@ensure_csrf_cookie
def favorites(request):
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        products = wishlist.products.all().select_related("category")
    else:
        # For non-authenticated, the JS will handle it or we can show empty
        products = Product.objects.none()
    return render(request, "products/favorites.html", {"products": products})


@require_POST
def toggle_wishlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)

    data = json.loads(request.body)
    product_id = data.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(id=product.id).exists():
        wishlist.products.remove(product)
        added = False
    else:
        wishlist.products.add(product)
        added = True

    return JsonResponse({
        "added": added,
        "count": wishlist.products.count()
    })


def wishlist_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"ids": []})
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return JsonResponse({"ids": list(wishlist.products.values_list("id", flat=True))})


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
