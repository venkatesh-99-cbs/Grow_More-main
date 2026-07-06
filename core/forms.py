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
        fields = ("group", "title", "subtitle", "button_label", "button_url", "image", "theme", "animation_type", "is_active", "sort_order")

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
        return instance


class HeroGroupForm(forms.ModelForm):
    class Meta:
        model = HeroGroup
        fields = ("name", "title", "subtitle", "button_label", "button_url", "is_active", "sort_order")

