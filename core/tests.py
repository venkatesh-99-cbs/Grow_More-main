from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from offers.models import PromotionalOffer
from products.models import Category, Product


class CoreApiTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="API Category")
        self.product = Product.objects.create(
            name="API Product",
            category=self.category,
            description="API product",
            price=125,
            sizes=["M"],
            colors=["Blue"],
            stock=3,
            is_active=True,
        )

    def test_products_api_supports_shop_filter_payload(self):
        response = self.client.get("/api/products/", {"q": "API Product", "category": "all", "sort": "featured"})

        self.assertEqual(response.status_code, 200)
        product = response.json()["products"][0]
        self.assertEqual(product["url"], self.product.get_absolute_url())
        self.assertEqual(product["categoryName"], self.category.name)
        self.assertIn("originalPrice", product)
        self.assertIn("discountPercent", product)


class OfferPopupTemplateTests(TestCase):
    def test_active_offer_popup_renders_content_without_template_leaks(self):
        now = timezone.now()
        PromotionalOffer.objects.create(
            title="Popup Smoke Offer",
            description="Clean professional offer text.",
            offer_label="Limited Time Offer",
            discount_percent=20,
            starts_at=now - timedelta(minutes=5),
            ends_at=now + timedelta(days=1),
            offer_type="site_wide",
            show_on_homepage=True,
            cta_text="Shop Now",
            cta_link="/shop/",
            is_active=True,
        )

        response = self.client.get("/")
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Popup Smoke Offer")
        self.assertContains(response, "Clean professional offer text.")
        self.assertNotIn("{%", html)
        self.assertNotIn("{{ active_popup_offer", html)
