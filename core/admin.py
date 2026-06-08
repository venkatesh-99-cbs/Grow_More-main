from django.contrib import admin
from django.utils.html import format_html
from core.models import HeroBanner, HomepageSection

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'animation_type', 'is_active', 'sort_order', 'banner_preview')
    list_editable = ('is_active', 'sort_order', 'theme', 'animation_type')
    list_filter = ('theme', 'animation_type', 'is_active')
    search_fields = ('title', 'subtitle')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'button_label', 'button_url')
        }),
        ('Media', {
            'fields': ('image', 'image_url')
        }),
        ('Styling & Animation', {
            'fields': ('theme', 'animation_type', 'is_active', 'sort_order')
        }),
    )

    def banner_preview(self, obj):
        if obj.display_image:
            return format_html('<img src="{}" style="height:50px; border-radius:8px;">', obj.display_image)
        return "No Image"

@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
