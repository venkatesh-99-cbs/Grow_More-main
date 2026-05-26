from django import forms

from products.models import Category, Product


class ProductForm(forms.ModelForm):
    sizes_text = forms.CharField(help_text="Comma-separated sizes, e.g. S,M,L,XL")
    colors_text = forms.CharField(required=False, help_text="Comma-separated colors")

    class Meta:
        model = Product
        fields = (
            "name", "slug", "category", "description", "price", "discount_price",
            "stock", "is_active", "is_featured", "is_trending", "main_image",
            "image_url", "gallery_image_1", "gallery_image_2", "gallery_image_3",
            "gallery_url_1", "gallery_url_2", "gallery_url_3",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["sizes_text"].initial = ", ".join(self.instance.sizes)
            self.fields["colors_text"].initial = ", ".join(self.instance.colors)

    def clean_sizes_text(self):
        values = [item.strip() for item in self.cleaned_data["sizes_text"].split(",") if item.strip()]
        if not values:
            raise forms.ValidationError("Add at least one size.")
        return values

    def clean_colors_text(self):
        return [item.strip() for item in self.cleaned_data.get("colors_text", "").split(",") if item.strip()]

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        discount_price = cleaned_data.get("discount_price")
        if price is not None and price <= 0:
            self.add_error("price", "Price must be greater than zero.")
        if discount_price is not None:
            if discount_price <= 0:
                self.add_error("discount_price", "Discount price must be greater than zero.")
            elif price is not None and discount_price >= price:
                self.add_error("discount_price", "Discount price must be lower than the regular price.")
        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        product.sizes = self.cleaned_data["sizes_text"]
        product.colors = self.cleaned_data["colors_text"]
        if commit:
            product.save()
            self.save_m2m()
        return product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "description", "is_active", "sort_order")
