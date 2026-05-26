from django.contrib import admin
from django.utils.html import format_html

from core.models import HeroBanner


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "sort_order", "preview")
    list_editable = ("is_active", "sort_order")

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.display_image:
            return "-"
        return format_html('<img src="{}" style="height:46px;border-radius:6px;">', obj.display_image)

