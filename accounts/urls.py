from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.GrowMoreLoginView.as_view(), name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("addresses/add/", views.add_address, name="add_address"),
    path("addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),
]
