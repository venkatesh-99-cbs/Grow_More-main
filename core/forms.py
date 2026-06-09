from django import forms

from core.models import HeroBanner, HeroGroup


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
    website = forms.CharField(required=False, widget=forms.HiddenInput)


class HeroBannerForm(forms.ModelForm):
    class Meta:
        model = HeroBanner
        fields = ("group", "title", "subtitle", "button_label", "button_url", "image", "image_url", "theme", "animation_type", "is_active", "sort_order")


class HeroGroupForm(forms.ModelForm):
    class Meta:
        model = HeroGroup
        fields = ("name", "title", "subtitle", "button_label", "button_url", "is_active", "sort_order")

