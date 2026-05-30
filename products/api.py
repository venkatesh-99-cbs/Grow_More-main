"""
Product filtering API endpoints
Handles advanced product filtering with brand, category, color, size, and price filters
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, F, DecimalField, Case, When, Value
import json

from products.models import Product, Brand, Category, ColorVariant, SizeStock


@csrf_exempt
@require_http_methods(["GET"])
def filter_products(request):
    """
    Advanced product filtering API endpoint
    
    Query Parameters:
    - brands: Comma-separated brand IDs
    - categories: Comma-separated category IDs
    - colors: Comma-separated color IDs
    - sizes: Comma-separated sizes (XS, S, M, L, XL, 2XL, 3XL, 4XL)
    - price_min: Minimum price
    - price_max: Maximum price
    - search: Search query for product name/description
    - page: Page number (default: 1)
    - page_size: Items per page (default: 12)
    """
    
    try:
        # Get filter parameters
        brands = request.GET.get('brands', '').split(',') if request.GET.get('brands') else []
        categories = request.GET.get('categories', '').split(',') if request.GET.get('categories') else []
        colors = request.GET.get('colors', '').split(',') if request.GET.get('colors') else []
        sizes = request.GET.get('sizes', '').split(',') if request.GET.get('sizes') else []
        price_min = request.GET.get('price_min')
        price_max = request.GET.get('price_max')
        search = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 12))
        
        # Start with all active products
        queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
        
        # Apply brand filter
        if brands and brands != ['']:
            brands = [b for b in brands if b]  # Remove empty strings
            if brands:
                queryset = queryset.filter(brand_id__in=brands)
        
        # Apply category filter
        if categories and categories != ['']:
            categories = [c for c in categories if c]  # Remove empty strings
            if categories:
                queryset = queryset.filter(category_id__in=categories)
        
        # Apply color filter (M2M)
        if colors and colors != ['']:
            colors = [c for c in colors if c]  # Remove empty strings
            if colors:
                queryset = queryset.filter(colors__id__in=colors).distinct()
        
        # Apply size filter (through SizeStock)
        if sizes and sizes != ['']:
            sizes = [s for s in sizes if s]  # Remove empty strings
            if sizes:
                # Filter products that have stock for selected sizes
                queryset = queryset.filter(
                    sizestock__size__in=sizes,
                    sizestock__stock_quantity__gt=0
                ).distinct()
        
        # Apply price filter (use discount_price if available, else price)
        if price_min:
            try:
                price_min = float(price_min)
                queryset = queryset.filter(
                    Q(discount_price__gte=price_min) | Q(discount_price__isnull=True, price__gte=price_min)
                )
            except ValueError:
                pass
        
        if price_max:
            try:
                price_max = float(price_max)
                queryset = queryset.filter(
                    Q(discount_price__lte=price_max) | Q(discount_price__isnull=True, price__lte=price_max)
                )
            except ValueError:
                pass
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Count total results
        total_count = queryset.count()
        
        # Pagination
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serialize products
        products = []
        for product in page_obj:
            product_data = {
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'description': product.description[:100] if product.description else '',
                'brand': product.brand.name if product.brand else None,
                'category': product.category.name if product.category else None,
                'current_price': float(product.current_price),
                'original_price': float(product.original_price) if product.original_price else None,
                'discount_percentage': product.discount_percent or 0,
                'image': product.main_image_url,
                'in_stock': product.in_stock,
                'is_featured': product.is_featured,
                'is_trending': product.is_trending,
                'colors': [
                    {
                        'id': color.id,
                        'name': color.name,
                        'hex_code': color.hex_code
                    }
                    for color in product.colors.all()
                ],
                'available_sizes': [
                    {
                        'size': ss.size,
                        'stock': ss.available_quantity,
                        'is_low_stock': ss.is_low_stock,
                        'is_out_of_stock': ss.is_out_of_stock
                    }
                    for ss in product.size_stocks.filter(stock_quantity__gt=0)
                ],
            }
            products.append(product_data)
        
        # Build pagination info
        pagination = {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': total_count,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'start_index': page_obj.start_index(),
            'end_index': page_obj.end_index(),
        }
        
        return JsonResponse({
            'success': True,
            'products': products,
            'count': len(products),
            'total_count': total_count,
            'pagination': pagination,
            'filters': {
                'brands': brands,
                'categories': categories,
                'colors': colors,
                'sizes': sizes,
                'price_min': price_min,
                'price_max': price_max,
                'search': search,
            }
        }, safe=True)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def get_filter_options(request):
    """
    Get available filter options (brands, categories, colors, sizes, price range)
    Useful for populating filter UI
    """
    
    try:
        # Get all active products
        products = Product.objects.filter(is_active=True)
        
        # Brands
        brands = Brand.objects.filter(is_active=True).values('id', 'name', 'slug').order_by('sort_order')
        
        # Categories
        categories = Category.objects.filter(is_active=True).values('id', 'name', 'slug').order_by('name')
        
        # Colors
        colors = ColorVariant.objects.filter(is_active=True).values('id', 'name', 'hex_code').order_by('sort_order')
        
        # Sizes (from SizeStock)
        sizes = (
            SizeStock.objects
            .filter(product__is_active=True, stock_quantity__gt=0)
            .values_list('size', flat=True)
            .distinct()
            .order_by('size')
        )
        
        # Price range - calculate from actual price field
        from django.db.models import Min, Max, Case, When, DecimalField
        price_stats = products.aggregate(
            min_price=Min(
                Case(
                    When(discount_price__isnull=False, then='discount_price'),
                    default='price',
                    output_field=DecimalField(),
                )
            ),
            max_price=Max(
                Case(
                    When(discount_price__isnull=False, then='discount_price'),
                    default='price',
                    output_field=DecimalField(),
                )
            ),
        )
        
        return JsonResponse({
            'success': True,
            'brands': list(brands),
            'categories': list(categories),
            'colors': list(colors),
            'sizes': list(sizes),
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 10000),
            }
        }, safe=True)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def search_products(request):
    """
    Simple product search endpoint
    Query parameter: q (search query)
    """
    
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({
                'success': True,
                'products': [],
                'message': 'Please enter at least 2 characters to search'
            })
        
        # Search products
        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('brand', 'category')[:20]  # Limit to 20 results
        
        # Serialize
        results = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'image': p.main_image_url,
                'price': float(p.current_price),
                'brand': p.brand.name if p.brand else None,
                'category': p.category.name if p.category else None,
            }
            for p in products
        ]
        
        return JsonResponse({
            'success': True,
            'products': results,
            'count': len(results),
            'query': query
        }, safe=True)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=400)
