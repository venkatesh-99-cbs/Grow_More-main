from django.urls import path

from orders import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_api, name="cart_api"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/items/<int:pk>/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/items/<int:pk>/remove/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/verify/", views.verify_payment, name="verify_payment"),
    path("orders/<str:order_number>/", views.order_detail, name="detail"),
    path("orders/<str:order_number>/success/", views.order_success, name="success"),
    path("orders/<str:order_number>/payment-receipt/", views.download_payment_receipt, name="download_payment_receipt"),
    path("orders/<str:order_number>/shipping-sheet/", views.download_shipping_sheet, name="download_shipping_sheet"),
    path("orders/<str:order_number>/invoice/", views.download_invoice, name="download_invoice"),
    path("orders/<str:order_number>/delivery-sheet/", views.download_delivery_sheet, name="download_delivery_sheet"),
]
