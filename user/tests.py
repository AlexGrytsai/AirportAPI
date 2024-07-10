from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class UserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword"
        )

    def test_user_view_permissions(self):
        response = self.client.get(reverse("user:users"))

        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user:users"))

        self.assertEqual(response.status_code, 403)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse("user:users"))

        self.assertEqual(response.status_code, 200)

        self.user.is_staff = False
        self.user.save()
        self.client.logout()
        response = self.client.post(
            reverse("users:users"),
            data={
                "email": "test2@example.com", "password": "testpassword"
            }
        )

        self.assertEqual(response.status_code, 201)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("user:users"))

        self.assertEqual(response.status_code, 403)

        self.user.is_staff = True
        self.user.save()
        response = self.client.post(
            reverse("user:users"),
            data={
                "email": "test3@example.com", "password": "testpassword"
            }
        )


class ManageUserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="testpassword"
        )

    def test_manage_user_view_get_object(self):
        response = self.client.get(reverse("user:me"))
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("user:me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test@example.com")
