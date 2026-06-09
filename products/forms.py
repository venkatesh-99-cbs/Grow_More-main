from django import forms

from products.cloudinary_utils import CloudinaryUploadError, delete_product_image, upload_product_image
from products.models import Brand, Category, Product, SizeStock, validate_hex_color


class ProductForm(forms.ModelForm):
    sizes_list = forms.MultipleChoiceField(
        choices=SizeStock.SIZE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Available Sizes"
    )
    color_hex = forms.CharField(
        max_length=7,
        help_text="Single HEX color only, for example #3498DB.",
        validators=[validate_hex_color],
        widget=forms.TextInput(attrs={"placeholder": "#3498DB", "pattern": r"#[0-9A-Fa-f]{6}"}),
    )

    class Meta:
        model = Product
        fields = (
            "name", "slug", "category", "description", "price", "discount_price",
            "stock", "brand", "color_hex", "color_name", "is_active", "is_featured", "is_trending", "main_image",
            "gallery_image_1", "gallery_image_2", "gallery_image_3",
            "gallery_url_1", "gallery_url_2", "gallery_url_3",
        )
        widgets = {
            "main_image": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"}),
            "gallery_image_1": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"}),
            "gallery_image_2": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"}),
            "gallery_image_3": forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["sizes_list"].initial = self.instance.sizes

    def clean_sizes_list(self):
        values = self.cleaned_data.get("sizes_list")
        if not values:
            raise forms.ValidationError("Select at least one size.")
        return values

    def clean_color_hex(self):
        return self.cleaned_data["color_hex"].upper()

    def _validate_image(self, field_name):
        image = self.cleaned_data.get(field_name)
        if not image:
            return image

        allowed_content_types = {"image/jpeg", "image/png", "image/webp"}
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        name = (getattr(image, "name", "") or "").lower()
        content_type = getattr(image, "content_type", "")
        max_size = 5 * 1024 * 1024

        if content_type and content_type not in allowed_content_types:
            raise forms.ValidationError("Upload a JPG, JPEG, PNG, or WEBP image.")
        if not any(name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Upload a JPG, JPEG, PNG, or WEBP image.")
        if image.size > max_size:
            raise forms.ValidationError("Image must be 5 MB or smaller.")
        return image

    def clean_main_image(self):
        return self._validate_image("main_image")

    def clean_gallery_image_1(self):
        return self._validate_image("gallery_image_1")

    def clean_gallery_image_2(self):
        return self._validate_image("gallery_image_2")

    def clean_gallery_image_3(self):
        return self._validate_image("gallery_image_3")

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
        product.sizes = self.cleaned_data["sizes_list"]

        # Handle size stock management from post data if available
        # This is for the custom dashboard
        size_stock_data = {}
        for key, value in self.data.items():
            if key.startswith("size_stock_"):
                size = key.replace("size_stock_", "")
                if size in product.sizes:
                    try:
                        size_stock_data[size] = int(value)
                    except ValueError:
                        pass

        uploaded_main = self.cleaned_data.get("main_image")
        if uploaded_main:
            old_public_id = self.instance.cloudinary_public_id if self.instance and self.instance.pk else None
            try:
                upload_result = upload_product_image(uploaded_main)
            except CloudinaryUploadError as exc:
                raise forms.ValidationError(str(exc)) from exc
            if upload_result:
                product.image_url = upload_result.secure_url
                product.cloudinary_public_id = upload_result.public_id
                product.main_image = ""
                if old_public_id and old_public_id != upload_result.public_id:
                    delete_product_image(old_public_id)

        if commit:
            product.save()
            self.save_m2m()
            # Update SizeStock objects
            from products.models import SizeStock
            for size, stock_qty in size_stock_data.items():
                SizeStock.objects.update_or_create(
                    product=product,
                    size=size,
                    defaults={"stock_quantity": stock_qty}
                )
        return product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "slug", "description", "is_active", "sort_order")


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ("name", "slug", "description", "is_active", "sort_order")
