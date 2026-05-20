from django.urls import path

from products import views

app_name = "products"

urlpatterns = [
    path("shop/", views.shop, name="shop"),
    path("products/<slug:slug>/", views.detail, name="detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("api/products/", views.product_api, name="api"),
]
