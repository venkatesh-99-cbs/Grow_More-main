from django.urls import path

from offers import views

app_name = "offers"

urlpatterns = [
    path("api/offers/active/", views.active_offer_api, name="active_api"),
]
