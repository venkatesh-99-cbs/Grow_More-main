from django.db import models
from django.urls import reverse

from core.validators import validate_store_image


class HeroBanner(models.Model):
    title = models.CharField(max_length=160)
    subtitle = models.TextField(blank=True)
    button_label = models.CharField(max_length=80, default="Shop Now")
    button_url = models.CharField(max_length=255, default="/shop/")
    image = models.FileField(upload_to="hero/", validators=[validate_store_image], blank=True)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url


class HomepageSection(models.Model):
    SECTION_TYPES = [
        ("featured", "Featured Products"),
        ("trending", "Trending Products"),
        ("collection", "Collection"),
    ]

    title = models.CharField(max_length=120)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default="featured")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    limit = models.PositiveIntegerField(default=4)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("dashboard:homepage")
