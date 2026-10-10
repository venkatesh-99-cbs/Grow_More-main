from django import forms

from offers.models import PromotionalOffer


DATETIME_LOCAL_FORMAT = "%Y-%m-%dT%H:%M"


class PromotionalOfferForm(forms.ModelForm):
    class Meta:
        model = PromotionalOffer
        fields = (
            "title", "slug", "description", "offer_label", "highlight_text", "discount_percent",
            "starts_at", "ends_at", "countdown_end", "cta_text", "cta_link", "image",
            "is_active", "show_on_homepage", "floating_ball_enabled",
            "permanent_dismiss_allowed", "display_priority", "offer_type", "products", "categories",
        )
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DATETIME_LOCAL_FORMAT),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DATETIME_LOCAL_FORMAT),
            "countdown_end": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DATETIME_LOCAL_FORMAT),
            "products": forms.SelectMultiple(attrs={"size": 8}),
            "categories": forms.SelectMultiple(attrs={"size": 5}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("starts_at", "ends_at", "countdown_end"):
            self.fields[name].input_formats = [DATETIME_LOCAL_FORMAT]

    def clean(self):
        cleaned_data = super().clean()
        offer_type = cleaned_data.get("offer_type")
        products = cleaned_data.get("products")
        categories = cleaned_data.get("categories")
        if offer_type == "product" and not products:
            self.add_error("products", "Select at least one product for a product-specific offer.")
        if offer_type == "category" and not categories:
            self.add_error("categories", "Select at least one category for a category-based offer.")
        return cleaned_data

    def clean_cta_link(self):
        value = self.cleaned_data["cta_link"].strip()
        if not (value.startswith("/") or value.startswith("https://") or value.startswith("http://")):
            raise forms.ValidationError("CTA link must be a local path or full URL.")
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        file_obj = self.cleaned_data.get("image")
        if file_obj:
            from products.cloudinary_utils import upload_product_image, cloudinary_is_configured
            if cloudinary_is_configured():
                try:
                    result = upload_product_image(file_obj)
                    if result:
                        instance.image_url = result.secure_url
                        instance.image = ""
                except Exception:
                    pass
        if commit:
            instance.save()
            self.save_m2m()
        return instance
