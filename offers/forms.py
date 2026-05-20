from django import forms

from offers.models import PromotionalOffer


class PromotionalOfferForm(forms.ModelForm):
    class Meta:
        model = PromotionalOffer
        fields = (
            "title", "slug", "description", "offer_label", "highlight_text", "discount_percent",
            "starts_at", "ends_at", "countdown_end", "cta_text", "cta_link", "image", "image_url",
            "is_active", "site_wide", "show_on_homepage", "floating_ball_enabled",
            "permanent_dismiss_allowed", "display_priority", "offer_type", "products", "categories",
        )
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "countdown_end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "products": forms.SelectMultiple(attrs={"size": 8}),
            "categories": forms.SelectMultiple(attrs={"size": 5}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_cta_link(self):
        value = self.cleaned_data["cta_link"].strip()
        if not (value.startswith("/") or value.startswith("https://") or value.startswith("http://")):
            raise forms.ValidationError("CTA link must be a local path or full URL.")
        return value
