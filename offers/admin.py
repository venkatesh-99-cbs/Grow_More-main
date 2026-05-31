from django.contrib import admin
from offers.models import PromotionalOffer

@admin.register(PromotionalOffer)
class PromotionalOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_type', 'discount_percent', 'is_active', 'starts_at', 'ends_at')
    list_filter = ('offer_type', 'is_active', 'starts_at', 'ends_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'description', 'offer_label', 'highlight_text')
        }),
        ('Discount & Scope', {
            'fields': ('discount_percent', 'offer_type', 'products', 'categories', 'brands')
        }),
        ('Schedule', {
            'fields': ('starts_at', 'ends_at', 'countdown_end')
        }),
        ('Appearance', {
            'fields': ('image', 'image_url', 'cta_text', 'cta_link', 'display_priority', 'show_on_homepage', 'floating_ball_enabled')
        }),
        ('Settings', {
            'fields': ('is_active', 'permanent_dismiss_allowed')
        }),
    )
    filter_horizontal = ('products', 'categories', 'brands')
