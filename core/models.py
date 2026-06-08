from django.db import models
from django.urls import reverse

from core.validators import validate_store_image


class HeroGroup(models.Model):
    """
    Groups multiple hero banners together.
    Banners in the same group share the same text content.
    """
    name = models.CharField(max_length=100, help_text="Example: Summer Collection")
    title = models.CharField(max_length=160)
    subtitle = models.TextField(blank=True)
    button_label = models.CharField(max_length=80, default="Shop Now")
    button_url = models.CharField(max_length=255, default="/shop/")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "Hero Group"
        verbose_name_plural = "Hero Groups"

    def __str__(self):
        return self.name


class HeroBanner(models.Model):
    THEME_CHOICES = [
        ('summer', 'Summer Theme'),
        ('winter', 'Winter Theme'),
        ('luxury', 'Luxury Theme'),
        ('festival', 'Festival Theme'),
        ('streetwear', 'Streetwear Theme'),
    ]

    ANIMATION_CHOICES = [
        ('fade', 'Fade In'),
        ('slide-up', 'Slide Up'),
        ('scale', 'Scale In'),
        ('parallax', 'Parallax Effect'),
    ]

    group = models.ForeignKey(HeroGroup, on_delete=models.CASCADE, related_name='banners', null=True, blank=True)
    title = models.CharField(max_length=160, blank=True, help_text="Overridden by group title if group is set.")
    subtitle = models.TextField(blank=True, help_text="Overridden by group subtitle if group is set.")
    button_label = models.CharField(max_length=80, default="Shop Now", blank=True)
    button_url = models.CharField(max_length=255, default="/shop/", blank=True)
    image = models.FileField(upload_to="hero/", validators=[validate_store_image], blank=True)
    image_url = models.URLField(blank=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='summer')
    animation_type = models.CharField(max_length=20, choices=ANIMATION_CHOICES, default='fade')
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.display_title

    @property
    def display_title(self):
        return self.group.title if self.group else self.title

    @property
    def display_subtitle(self):
        return self.group.subtitle if self.group else self.subtitle

    @property
    def display_button_label(self):
        return self.group.button_label if self.group else self.button_label

    @property
    def display_button_url(self):
        return self.group.button_url if self.group else self.button_url

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
