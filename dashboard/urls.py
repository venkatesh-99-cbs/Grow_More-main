from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("products/", views.products, name="products"),
    path("products/new/", views.product_form, name="product_create"),
    path("products/<int:pk>/edit/", views.product_form, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("categories/", views.categories, name="categories"),
    path("categories/<int:pk>/edit/", views.categories, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("brands/", views.brands, name="brands"),
    path("brands/<int:pk>/edit/", views.brands, name="brand_edit"),
    path("brands/<int:pk>/delete/", views.brand_delete, name="brand_delete"),
    path("homepage/", views.homepage, name="homepage"),
    path("homepage/groups/<int:pk>/edit/", views.homepage, name="group_edit"),
    path("homepage/groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
    path("homepage/banners/new/", views.banner_create, name="banner_create"),
    path("homepage/banners/<int:pk>/delete/", views.banner_delete, name="banner_delete"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:pk>/status/", views.order_status, name="order_status"),
    path("orders/<int:pk>/payment-receipt/", views.admin_download_payment_receipt, name="admin_download_payment_receipt"),
    path("orders/<int:pk>/shipping-sheet/", views.admin_download_shipping_sheet, name="admin_download_shipping_sheet"),
    path("orders/<int:pk>/invoice/", views.admin_download_invoice, name="admin_download_invoice"),
    path("orders/<int:pk>/delivery-sheet/", views.admin_download_delivery_sheet, name="admin_download_delivery_sheet"),
    path("customers/", views.customers, name="customers"),
    path("payments/", views.payments, name="payments"),
    path("offers/", views.offers, name="offers"),
    path("offers/new/", views.offer_form, name="offer_create"),
    path("offers/<int:pk>/edit/", views.offer_form, name="offer_edit"),
    path("offers/<int:pk>/delete/", views.offer_delete, name="offer_delete"),
]
