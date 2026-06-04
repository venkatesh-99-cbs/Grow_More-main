from django.contrib import admin
from django.utils.html import format_html

from products.models import Brand, Category, ColorVariant, Product, SizeStock


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order", "brand_logo")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "logo_preview")
    fieldsets = (
        ("Brand Info", {"fields": ("name", "slug", "description")}),
        ("Media", {"fields": ("logo", "logo_preview")}),
        ("Details", {"fields": ("website", "is_active", "sort_order")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Logo")
    def brand_logo(self, obj):
        if not obj.logo:
            return "-"
        return format_html('<img src="{}" style="height:30px;width:auto;max-width:100px;object-fit:contain;border-radius:4px;">', obj.logo.url)

    @admin.display(description="Logo Preview")
    def logo_preview(self, obj):
        if not obj.logo:
            return "Upload a brand logo"
        return format_html('<img src="{}" style="max-height:150px;max-width:300px;object-fit:contain;border-radius:8px;">', obj.logo.url)


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ("name", "hex_code", "color_swatch", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "hex_code")
    ordering = ("sort_order", "name")

    @admin.display(description="Color")
    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:24px;height:24px;background-color:{};border-radius:4px;border:1px solid #ccc;vertical-align:middle;"></span>',
            obj.hex_code
        )


class SizeStockInline(admin.TabularInline):
    model = SizeStock
    extra = 0
    fields = ("size", "stock_quantity", "reserved_quantity", "available_quantity", "is_out_of_stock")
    readonly_fields = ("available_quantity", "is_out_of_stock")
    ordering = ["size"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "current_price", "color_preview", "total_stock", "is_active", "is_featured", "is_trending", "preview")
    list_filter = ("brand", "category", "is_active", "is_featured", "is_trending")
    list_editable = ("is_active", "is_featured", "is_trending")
    search_fields = ("name", "description", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    inlines = (SizeStockInline,)
    fieldsets = (
        ("Basics", {"fields": ("name", "slug", "category", "brand", "description")}),
        ("Pricing", {"fields": ("price", "discount_price")}),
        ("Stock Management", {"fields": ("stock", "sizes", "color_hex")}),
        ("Visibility", {"fields": ("is_active", "is_featured", "is_trending")}),
        ("Images", {"fields": ("main_image", "image_url", "cloudinary_public_id", "gallery_image_1", "gallery_image_2", "gallery_image_3", "gallery_url_1", "gallery_url_2", "gallery_url_3", "image_preview")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Color")
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:6px;"><span style="display:inline-block;width:22px;height:22px;background:{};border-radius:999px;border:1px solid #ccc;"></span>{}</span>',
            obj.safe_color_hex,
            obj.safe_color_hex,
        )

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.main_image_url:
            return "-"
        return format_html('<img src="{}" style="height:46px;width:46px;object-fit:cover;border-radius:6px;">', obj.main_image_url)

    @admin.display(description="Total Stock")
    def total_stock(self, obj):
        total = obj.get_total_stock()
        return format_html(
            '<span style="font-weight:bold;color:{};">{}</span>',
            '#2fa66f' if total > 0 else '#d9534f',
            total
        )

    @admin.display(description="Current Image")
    def image_preview(self, obj):
        if not obj or not obj.main_image_url:
            return "Upload an image or add an image URL."
        return format_html('<img src="{}" style="max-height:180px;border-radius:10px;">', obj.main_image_url)


@admin.register(SizeStock)
class SizeStockAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "stock_quantity", "reserved_quantity", "available_qty", "status")
    list_filter = ("product__category", "size", "product__brand")
    search_fields = ("product__name",)
    ordering = ("-updated_at",)
    readonly_fields = ("available_quantity", "is_out_of_stock", "is_low_stock", "updated_at")

    @admin.display(description="Available")
    def available_qty(self, obj):
        color = '#2fa66f' if not obj.is_out_of_stock else '#d9534f'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.available_quantity)

    @admin.display(description="Status")
    def status(self, obj):
        if obj.is_out_of_stock:
            badge_color = '#d9534f'
            status_text = 'Out of Stock'
        elif obj.is_low_stock:
            badge_color = '#f0ad4e'
            status_text = 'Low Stock'
        else:
            badge_color = '#2fa66f'
            status_text = 'In Stock'
        return format_html(
            '<span style="background-color:{};color:white;padding:3px 8px;border-radius:12px;font-weight:bold;font-size:0.85em;">{}</span>',
            badge_color, status_text
        )
