from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pass", is_staff=True)

    def test_homepage_dashboard_has_no_section_creation_form(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:homepage"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Add Section")
        self.assertNotContains(response, "section_create")

    def test_removed_section_create_route_returns_not_found(self):
        self.client.force_login(self.staff)

        response = self.client.post("/dashboard/homepage/sections/new/")

        self.assertEqual(response.status_code, 404)
