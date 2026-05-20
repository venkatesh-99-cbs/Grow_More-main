from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.validators import validate_store_image


class PromotionalOffer(models.Model):
    OFFER_TYPES = [
        ("site_wide", "Site-wide"),
        ("homepage", "Homepage only"),
        ("product", "Product specific"),
        ("category", "Category based"),
        ("trending", "Trending products"),
        ("featured", "Featured products"),
    ]

    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    offer_label = models.CharField(max_length=80, default="Limited Time Offer")
    highlight_text = models.CharField(max_length=120, blank=True)
    discount_percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    countdown_end = models.DateTimeField(blank=True, null=True, help_text="Leave blank to use offer end time.")
    cta_text = models.CharField(max_length=80, default="Shop Now")
    cta_link = models.CharField(max_length=255, default="/shop/")
    image = models.FileField(upload_to="offers/", validators=[validate_store_image], blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    site_wide = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=True)
    floating_ball_enabled = models.BooleanField(default=True)
    permanent_dismiss_allowed = models.BooleanField(default=True)
    display_priority = models.PositiveIntegerField(default=0)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default="site_wide")
    products = models.ManyToManyField("products.Product", blank=True, related_name="assigned_offers")
    categories = models.ManyToManyField("products.Category", blank=True, related_name="assigned_offers")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_priority", "-starts_at"]
        indexes = [
            models.Index(fields=["is_active", "starts_at", "ends_at"]),
            models.Index(fields=["offer_type", "display_priority"]),
        ]

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "Offer end time must be after start time."})
        if self.countdown_end and self.countdown_end > self.ends_at:
            raise ValidationError({"countdown_end": "Countdown end cannot be after offer end time."})
        if self.offer_type == "site_wide":
            self.site_wide = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        now = timezone.now()
        return self.is_active and self.starts_at <= now <= self.ends_at

    @property
    def countdown_target(self):
        return self.countdown_end or self.ends_at

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    def get_absolute_url(self):
        return reverse("dashboard:offer_edit", kwargs={"pk": self.pk})

    def discount_price_for(self, price):
        discount = Decimal(self.discount_percent) / Decimal("100")
        return (price * (Decimal("1.00") - discount)).quantize(Decimal("0.01"))

    def applies_to_product(self, product):
        if not self.is_current:
            return False
        if self.site_wide or self.offer_type == "site_wide":
            return True
        if self.offer_type == "homepage" and product.is_featured:
            return True
        if self.offer_type == "product":
            return any(item.pk == product.pk for item in self.products.all())
        if self.offer_type == "category":
            return any(item.pk == product.category_id for item in self.categories.all())
        if self.offer_type == "trending":
            return product.is_trending
        if self.offer_type == "featured":
            return product.is_featured
        return False
