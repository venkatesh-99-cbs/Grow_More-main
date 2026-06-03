from django.urls import path

from products import views, api

app_name = "products"

urlpatterns = [
    path("shop/", views.shop, name="shop"),
    path("products/<slug:slug>/", views.detail, name="detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("api/products/", views.product_api, name="api"),
    path("api/wishlist/", views.wishlist_api, name="wishlist_api"),
    path("api/wishlist/toggle/", views.toggle_wishlist, name="wishlist_toggle"),
    
    # Advanced filtering API
    path("api/filter/", api.filter_products, name="api_filter"),
    path("api/filter-options/", api.get_filter_options, name="api_filter_options"),
    path("api/search/", api.search_products, name="api_search"),
]
