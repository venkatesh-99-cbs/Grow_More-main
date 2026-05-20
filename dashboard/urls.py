from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("products/", views.products, name="products"),
    path("products/new/", views.product_form, name="product_create"),
    path("products/<int:pk>/edit/", views.product_form, name="product_edit"),
    path("categories/", views.categories, name="categories"),
    path("homepage/", views.homepage, name="homepage"),
    path("homepage/banners/new/", views.banner_create, name="banner_create"),
    path("homepage/banners/<int:pk>/delete/", views.banner_delete, name="banner_delete"),
    path("homepage/sections/new/", views.section_create, name="section_create"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:pk>/status/", views.order_status, name="order_status"),
    path("customers/", views.customers, name="customers"),
    path("payments/", views.payments, name="payments"),
    path("offers/", views.offers, name="offers"),
    path("offers/new/", views.offer_form, name="offer_create"),
    path("offers/<int:pk>/edit/", views.offer_form, name="offer_edit"),
    path("offers/<int:pk>/delete/", views.offer_delete, name="offer_delete"),
]
