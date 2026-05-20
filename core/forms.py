from django import forms

from core.models import HeroBanner, HomepageSection


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))
    website = forms.CharField(required=False, widget=forms.HiddenInput)


class HeroBannerForm(forms.ModelForm):
    class Meta:
        model = HeroBanner
        fields = ("title", "subtitle", "button_label", "button_url", "image", "image_url", "is_active", "sort_order")


class HomepageSectionForm(forms.ModelForm):
    class Meta:
        model = HomepageSection
        fields = ("title", "section_type", "is_active", "sort_order", "limit")
