from django.contrib import admin
from django.utils.html import format_html
from core.models import HeroGroup, HeroBanner, HomepageSection

class HeroBannerInline(admin.TabularInline):
    model = HeroBanner
    extra = 1
    fields = ('image', 'image_url', 'theme', 'animation_type', 'is_active', 'sort_order')

@admin.register(HeroGroup)
class HeroGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    inlines = [HeroBannerInline]

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('display_title', 'group', 'theme', 'animation_type', 'is_active', 'sort_order', 'banner_preview')
    list_editable = ('is_active', 'sort_order', 'theme', 'animation_type')
    list_filter = ('group', 'theme', 'animation_type', 'is_active')
    search_fields = ('title', 'subtitle', 'group__name', 'group__title')

    fieldsets = (
        ('Grouping', {
            'fields': ('group',)
        }),
        ('Overriding Content (if no group)', {
            'fields': ('title', 'subtitle', 'button_label', 'button_url'),
            'description': 'These fields are ignored if a group is selected above.'
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

    def display_title(self, obj):
        return obj.display_title
    display_title.short_description = 'Title'

@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
