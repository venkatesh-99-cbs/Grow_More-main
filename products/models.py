from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.validators import validate_store_image


class Brand(models.Model):
    """Premium brand management for Grow More fashion line."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brands/logos/", validators=[validate_store_image], blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "brand"
            slug = base_slug
            counter = 2
            while Brand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ColorVariant(models.Model):
    """Color variants for products with hex codes and visual representation."""
    PRESET_COLORS = [
        ('Bright Blue', '#51e2f5'),
        ('Blue Green', '#9df9ef'),
        ('Dusty White', '#edf756'),
        ('Pink Sand', '#ffa8b6'),
        ('Dark Sand', '#a28089'),
        ('Ink', '#3a2f33'),
        ('Black', '#000000'),
        ('White', '#ffffff'),
        ('Navy', '#001f3f'),
        ('Ocean Blue', '#0066cc'),
        ('Sunset Orange', '#ff6b35'),
        ('Forest Green', '#2d5016'),
        ('Cream', '#fffdd0'),
        ('Charcoal', '#36454f'),
    ]

    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, default='#51e2f5')  # Hex color code
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]
        unique_together = ("name", "hex_code")

    def __str__(self):
        return f"{self.name} ({self.hex_code})"

    def get_color_display(self):
        return {'name': self.name, 'hex': self.hex_code}


class SizeStock(models.Model):
    """Track stock levels by size for each product."""
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2X Large'),
        ('3XL', '3X Large'),
        ('4XL', '4X Large'),
    ]

    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='size_stocks')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'size')
        ordering = ['size']
        verbose_name = "Size Stock"
        verbose_name_plural = "Size Stocks"
        indexes = [
            models.Index(fields=['product', 'stock_quantity']),
        ]

    @property
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity

    @property
    def is_low_stock(self):
        return self.available_quantity <= self.low_stock_threshold

    @property
    def is_out_of_stock(self):
        return self.available_quantity <= 0

    def __str__(self):
        return f"{self.product.name} - Size {self.size}: {self.available_quantity} available"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "category"
            slug = base_slug
            counter = 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    """User wishlist for saving favorite products."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    products = models.ManyToManyField('Product', related_name="wishlisted_by", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


class Product(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sizes = models.JSONField(default=list, help_text="Example: ['S', 'M', 'L', 'XL']")
    colors = models.ManyToManyField(ColorVariant, blank=True, related_name="products")
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_trending = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    main_image = models.FileField(upload_to="products/main/", validators=[validate_store_image], blank=True)
    image_url = models.URLField(blank=True)
    gallery_image_1 = models.FileField(upload_to="products/gallery/", validators=[validate_store_image], blank=True)
    gallery_image_2 = models.FileField(upload_to="products/gallery/", validators=[validate_store_image], blank=True)
    gallery_image_3 = models.FileField(upload_to="products/gallery/", validators=[validate_store_image], blank=True)
    gallery_url_1 = models.URLField(blank=True)
    gallery_url_2 = models.URLField(blank=True)
    gallery_url_3 = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-is_trending", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["is_active", "is_trending"]),
            models.Index(fields=["brand"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "product"
            slug = base_slug
            counter = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"slug": self.slug})

    @property
    def current_price(self):
        from offers.services import price_for_product

        price, _offer = price_for_product(self)
        return price

    @property
    def original_price(self):
        if self.active_offer or self.discount_price:
            return self.price
        return self.price

    @property
    def discount_percent(self):
        if not self.original_price or self.current_price >= self.original_price:
            return 0
        return int(((self.original_price - self.current_price) / self.original_price) * 100)

    @property
    def active_offer(self):
        from offers.services import best_offer_for_product

        return best_offer_for_product(self)

    @property
    def offer_label(self):
        offer = self.active_offer
        return offer.offer_label if offer else "Limited Offer"

    @property
    def offer_highlight(self):
        offer = self.active_offer
        if offer and offer.highlight_text:
            return offer.highlight_text
        if self.discount_percent:
            return "Special pricing"
        return ""

    @property
    def offer_countdown_target(self):
        offer = self.active_offer
        return offer.countdown_target.isoformat() if offer else ""

    @property
    def main_image_url(self):
        url = ""
        if self.main_image:
            url = self.main_image.url
        else:
            url = self.image_url

        if url and "res.cloudinary.com" in url:
            # Add auto-optimization parameters
            if "/upload/" in url:
                return url.replace("/upload/", "/upload/f_auto,q_auto/")
        return url

    @property
    def gallery_images(self):
        raw_images = [self.main_image_url]
        files = [self.gallery_image_1, self.gallery_image_2, self.gallery_image_3]
        urls = [self.gallery_url_1, self.gallery_url_2, self.gallery_url_3]
        for file_obj, url in zip(files, urls):
            if file_obj:
                raw_images.append(file_obj.url)
            elif url:
                raw_images.append(url)

        processed_images = []
        for img in raw_images:
            if img:
                if "res.cloudinary.com" in img and "/upload/" in img:
                    processed_images.append(img.replace("/upload/", "/upload/f_auto,q_auto/"))
                else:
                    processed_images.append(img)
        return processed_images

    @property
    def in_stock(self):
        """Check if product has stock in any size."""
        return self.size_stocks.filter(stock_quantity__gt=0).exists() or self.stock > 0
    
    @property
    def size_stock_items(self):
        """Return list of (size, stock) tuples for template iteration."""
        items = []
        for size in self.sizes:
            try:
                items.append((size, self.size_stocks.get(size=size)))
            except:
                items.append((size, None))
        return items
    
    def get_size_stock(self, size):
        """Get stock for specific size."""
        try:
            return self.size_stocks.get(size=size)
        except:
            return None
    
    def get_total_stock(self):
        """Calculate total stock across all sizes."""
        return sum(ss.available_quantity for ss in self.size_stocks.all()) or self.stock
    
    def get_colors_display(self):
        """Get color variants for frontend display."""
        return [{'name': c.name, 'hex': c.hex_code} for c in self.colors.all()]

# Create your models here.
