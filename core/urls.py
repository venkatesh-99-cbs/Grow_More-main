from django.urls import path

from core import api, views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    # API endpoints for frontend dynamic content synchronization
    path("api/hero-banners/", api.api_hero_banners, name="api_hero_banners"),
    path("api/products/", api.api_products, name="api_products"),
    path("api/products/<int:product_id>/", api.api_product_detail, name="api_product_detail"),
    path("api/products/<int:product_id>/offer/", api.api_product_offer, name="api_product_offer"),
    path("api/homepage/sections/", api.api_homepage_sections, name="api_homepage_sections"),
    path("api/offers/active/", api.api_active_offers, name="api_active_offers"),
    path("api/offers/<int:offer_id>/", api.api_offer_detail, name="api_offer_detail"),
    path("api/categories/", api.api_categories, name="api_categories"),
    path("api/featured-products/", api.api_featured_products, name="api_featured_products"),
    path("api/deal-products/", api.api_deal_products, name="api_deal_products"),
    path("api/trending-products/", api.api_trending_products, name="api_trending_products"),
]
