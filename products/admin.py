from django.contrib import admin
from django.utils.html import format_html

from products.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "current_price", "stock", "is_active", "is_featured", "is_trending", "preview")
    list_filter = ("category", "is_active", "is_featured", "is_trending")
    list_editable = ("stock", "is_active", "is_featured", "is_trending")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Basics", {"fields": ("name", "slug", "category", "description")}),
        ("Pricing and stock", {"fields": ("price", "discount_price", "stock", "sizes", "colors")}),
        ("Visibility", {"fields": ("is_active", "is_featured", "is_trending")}),
        ("Images", {"fields": ("main_image", "image_url", "gallery_image_1", "gallery_image_2", "gallery_image_3", "gallery_url_1", "gallery_url_2", "gallery_url_3", "image_preview")}),
    )

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.main_image_url:
            return "-"
        return format_html('<img src="{}" style="height:46px;width:46px;object-fit:cover;border-radius:6px;">', obj.main_image_url)

    @admin.display(description="Current image")
    def image_preview(self, obj):
        if not obj or not obj.main_image_url:
            return "Upload an image or add an image URL."
        return format_html('<img src="{}" style="max-height:180px;border-radius:10px;">', obj.main_image_url)

# Register your models here.
