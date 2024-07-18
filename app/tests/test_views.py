from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from app.models import Airplane, AirplaneType
from app.serializers import (
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)
from app.views import AirplaneViewSet


class AirplaneViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com", password="testpassword", is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.airplane_type = AirplaneType.objects.create(name="Test Type")
        self.airplanes = [
            Airplane.objects.create(
                name="Boeing 747",
                code="AB123",
                rows=2,
                seats_in_row=4,
                airplane_type=self.airplane_type,
            ),
            Airplane.objects.create(
                name="Boeing 777",
                code="CD456",
                rows=3,
                seats_in_row=5,
                airplane_type=self.airplane_type,
            ),
        ]

    def test_access_to_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("app:airplane-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_to_view_authenticated(self):
        response = self.client.get(reverse("app:airplane-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_airplanes(self):
        response = self.client.get(reverse("app:airplane-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = AirplaneListSerializer(self.airplanes, many=True)
        self.assertEqual(response.data["results"], serializer.data)

    def test_serializer_class_action(self):
        view = AirplaneViewSet()
        view.action = "list"
        self.assertEqual(view.get_serializer_class(), AirplaneListSerializer)
        view.action = "retrieve"
        self.assertEqual(view.get_serializer_class(), AirplaneDetailSerializer)
        view.action = "create"
        self.assertEqual(view.get_serializer_class(), AirplaneSerializer)
        view.action = "update"
        self.assertEqual(view.get_serializer_class(), AirplaneSerializer)
        view.action = "partial_update"
        self.assertEqual(view.get_serializer_class(), AirplaneSerializer)
        view.action = "destroy"
        self.assertEqual(view.get_serializer_class(), AirplaneSerializer)

    def test_retrieve_airplane(self):
        airplane = self.airplanes[0]
        response = self.client.get(
            reverse("app:airplane-detail", kwargs={"pk": airplane.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = AirplaneDetailSerializer(airplane)
        self.assertEqual(response.data, serializer.data)

    def test_filter_airplanes_by_type(self):
        response = self.client.get(reverse("app:airplane-list") + "?type=Test Type")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_airplanes_by_total_seats(self):
        response = self.client.get(reverse("app:airplane-list") + "?total_seats=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_permissions(self):
        data = {
            "name": "Boeing 747",
            "code": "AB123",
            "rows": 5,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type,
        }
        self.user.is_staff = False
        self.user.save()
        response = self.client.post(reverse("app:airplane-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        airplane = self.airplanes[0]
        response = self.client.put(
            reverse("app:airplane-detail", kwargs={"pk": airplane.pk}), data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.save()

        response = self.client.post(reverse("app:airplane-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            reverse("app:airplane-detail", kwargs={"pk": airplane.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_airplane(self):
        self.user.is_staff = True

        data = {
            "name": "Airbus A380",
            "code": "EF789",
            "rows": 4,
            "seats_in_row": 8,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.post(reverse("app:airplane-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(pk=response.data["id"])
        self.assertEqual(airplane.name, data["name"])
        self.assertEqual(airplane.code, data["code"])
        self.assertEqual(airplane.rows, data["rows"])
        self.assertEqual(airplane.seats_in_row, data["seats_in_row"])
        self.assertEqual(airplane.airplane_type.pk, data["airplane_type"])

    def test_update_airplane(self):
        airplane = self.airplanes[0]
        data = {
            "name": "Boeing 787",
            "code": "AB123",
            "rows": 3,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.pk,
        }
        response = self.client.put(
            reverse(
                "app:airplane-detail", kwargs={"pk": airplane.pk}
            ), data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        airplane.refresh_from_db()
        self.assertEqual(airplane.name, data["name"])
        self.assertEqual(airplane.code, data["code"])
        self.assertEqual(airplane.rows, data["rows"])
        self.assertEqual(airplane.seats_in_row, data["seats_in_row"])

    def test_delete_airplane(self):
        airplane = self.airplanes[0]
        response = self.client.delete(
            reverse("app:airplane-detail", kwargs={"pk": airplane.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
