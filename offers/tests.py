from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from offers.models import PromotionalOffer
from offers.services import best_offer_for_product, price_for_product
from products.models import Category, Product


class OfferPricingTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Shirts")
        self.product = Product.objects.create(
            name="Linen Shirt",
            category=self.category,
            description="Breathable shirt",
            price=100,
            sizes=["M"],
            stock=10,
            is_active=True,
        )

    def create_offer(self, **overrides):
        now = timezone.now()
        data = {
            "title": "Summer Offer",
            "discount_percent": 20,
            "starts_at": now - timedelta(hours=1),
            "ends_at": now + timedelta(hours=1),
            "offer_type": "product",
            "is_active": True,
        }
        data.update(overrides)
        offer = PromotionalOffer.objects.create(**data)
        if offer.offer_type == "product":
            offer.products.set([self.product])
        return offer

    def test_product_offer_applies_when_it_beats_regular_price(self):
        offer = self.create_offer(discount_percent=25)

        price, active_offer = price_for_product(self.product)

        self.assertEqual(active_offer, offer)
        self.assertEqual(price, offer.discount_price_for(self.product.price))

    def test_weaker_offer_does_not_override_manual_discount_price(self):
        self.product.discount_price = 50
        self.product.save(update_fields=["discount_price"])
        self.create_offer(discount_percent=10)

        self.assertIsNone(best_offer_for_product(self.product))
        self.assertEqual(price_for_product(self.product), (self.product.discount_price, None))

    def test_category_offer_requires_matching_category(self):
        offer = self.create_offer(offer_type="category", discount_percent=30)
        offer.products.clear()
        offer.categories.set([self.category])

        self.assertEqual(best_offer_for_product(self.product), offer)
