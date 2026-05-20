from django.contrib import admin

from accounts.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "state", "postal_code", "is_default")
    list_filter = ("state", "is_default")
    search_fields = ("user__username", "user__email", "full_name", "phone", "city")

# Register your models here.
