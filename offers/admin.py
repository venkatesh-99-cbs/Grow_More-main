from django.contrib import admin
from django.utils.html import format_html

from offers.models import PromotionalOffer


@admin.register(PromotionalOffer)
class PromotionalOfferAdmin(admin.ModelAdmin):
    list_display = ("title", "offer_type", "discount_percent", "starts_at", "ends_at", "is_active", "display_priority")
    list_filter = ("offer_type", "is_active", "show_on_homepage", "floating_ball_enabled")
    list_editable = ("is_active", "display_priority")
    search_fields = ("title", "offer_label", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("products", "categories")
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Offer content", {"fields": ("title", "slug", "offer_label", "highlight_text", "description", "discount_percent")}),
        ("Schedule", {"fields": ("starts_at", "ends_at", "countdown_end")}),
        ("CTA and image", {"fields": ("cta_text", "cta_link", "image", "image_url", "image_preview")}),
        ("Visibility", {"fields": ("offer_type", "show_on_homepage", "floating_ball_enabled", "permanent_dismiss_allowed", "display_priority", "is_active")}),
        ("Assignments", {"fields": ("products", "categories")}),
    )

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if not obj or not obj.display_image:
            return "No promotional image configured."
        return format_html('<img src="{}" style="max-height:150px;border-radius:10px;">', obj.display_image)
