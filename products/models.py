from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.validators import validate_store_image


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


class Product(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sizes = models.JSONField(default=list, help_text="Example: ['S', 'M', 'L', 'XL']")
    colors = models.JSONField(default=list, blank=True, help_text="Example: ['Bright Blue', 'Pink Sand']")
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
        if self.main_image:
            return self.main_image.url
        return self.image_url

    @property
    def gallery_images(self):
        images = [self.main_image_url]
        files = [self.gallery_image_1, self.gallery_image_2, self.gallery_image_3]
        urls = [self.gallery_url_1, self.gallery_url_2, self.gallery_url_3]
        for file_obj, url in zip(files, urls):
            if file_obj:
                images.append(file_obj.url)
            elif url:
                images.append(url)
        return [img for img in images if img]

    @property
    def in_stock(self):
        return self.stock > 0

# Create your models here.
