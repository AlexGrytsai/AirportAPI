from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status
from app.models import Airplane, AirplaneType, Crew, Airport
from app.serializers import (
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    CrewListSerializer,
    CrewDetailSerializer,
    CrewSerializer, AirportListSerializer, AirportDetailSerializer,
    AirportSerializer,
)
from app.views import AirplaneViewSet, CrewViewSet, AirportViewSet


class AirplaneViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            is_staff=True
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
        response = self.client.get(
            reverse("app:airplane-list") + "?type=Test Type"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_airplanes_by_total_seats(self):
        response = self.client.get(
            reverse("app:airplane-list") + "?total_seats=10"
        )
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
            reverse(
                "app:airplane-detail", kwargs={"pk": airplane.pk}
            ), data
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


class CrewViewSetTests(TestCase):
    def setUp(self):
        self.view = CrewViewSet.as_view({"get": "list", "post": "create"})
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.crew_data = {
            "first_name": "John", "last_name": "Doe", "title": "Captain"
        }
        self.crew = Crew.objects.create(**self.crew_data)

    def test_access_to_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("app:crew-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_to_view_authenticated(self):
        response = self.client.get(reverse("app:crew-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_serializer_class_action(self):
        view = CrewViewSet()
        view.action = "list"
        self.assertEqual(view.get_serializer_class(), CrewListSerializer)
        view.action = "retrieve"
        self.assertEqual(view.get_serializer_class(), CrewDetailSerializer)
        view.action = "create"
        self.assertEqual(view.get_serializer_class(), CrewSerializer)
        view.action = "update"
        self.assertEqual(view.get_serializer_class(), CrewSerializer)
        view.action = "partial_update"
        self.assertEqual(view.get_serializer_class(), CrewSerializer)
        view.action = "destroy"
        self.assertEqual(view.get_serializer_class(), CrewSerializer)

    def test_permissions(self):
        self.user.is_staff = False
        self.user.save()

        response = self.client.get(reverse("app:crew-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("app:crew-list"), data=self.crew_data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.delete(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.patch(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.put(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True

        response = self.client.get(reverse("app:crew-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("app:crew-list"), data=self.crew_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            reverse("app:crew-detail", kwargs={"pk": self.crew.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_crew_instance(self):
        response = self.client.post(
            reverse("app:crew-list"), data=self.crew_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        crew = Crew.objects.get(pk=response.data["id"])
        self.assertEqual(crew.first_name, "John")
        self.assertEqual(crew.last_name, "Doe")
        self.assertEqual(crew.title, "Captain")


class AirportViewSetTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            is_staff=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.airport1 = Airport.objects.create(
            code="AAA",
            name="Anaa Airport",
            country="French Polynesia",
            city="Anaa",
            lat=-17.3595,
            lon=-145.494,
        )
        self.airport2 = Airport.objects.create(
            code="AAE",
            name="El Mellah Airport",
            country="Algeria",
            city="El Tarf",
            lat=36.8236,
            lon=7.8103,
        )

    def test_access_to_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("app:airport-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_class_action(self):
        view = AirportViewSet()
        view.action = "list"
        self.assertEqual(view.get_serializer_class(), AirportListSerializer)
        view.action = "retrieve"
        self.assertEqual(view.get_serializer_class(), AirportDetailSerializer)
        view.action = "create"
        self.assertEqual(view.get_serializer_class(), AirportSerializer)
        view.action = "update"
        self.assertEqual(view.get_serializer_class(), AirportSerializer)
        view.action = "partial_update"
        self.assertEqual(view.get_serializer_class(), AirportSerializer)
        view.action = "destroy"
        self.assertEqual(view.get_serializer_class(), AirportSerializer)

    @patch("app.serializers.AirportDetailSerializer.actual_weather")
    def test_permissions(self, mock_actual_weather=None):
        mock_actual_weather.return_value = {
            "localtime": "2024-07-18 10:00",
            "temperature": "25 Celsius (feels like 27 Celsius)",
            "condition": "Sunny",
        }

        data = {
            "code": "EEE",
            "name": "Anaa Airport",
            "country": "French Polynesia",
            "city": "Anaa",
            "lat": -17.3595,
            "lon": -145.494
        }

        def try_different_action() -> None:
            response = self.client.get(reverse("app:airport-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            response = self.client.get(
                reverse(
                    "app:airport-detail",
                    kwargs={"pk": self.airport1.pk}
                )
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            update_url = reverse(
                "app:airport-detail", kwargs={"pk": self.airport2.pk}
            )
            response = self.client.put(update_url, data=data)
            if self.user.is_staff:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(
                    response.status_code, status.HTTP_403_FORBIDDEN
                )

            if self.user.is_staff:
                data["code"] = "CCC"
            response = self.client.post(
                reverse("app:airport-list"), data=data
            )
            if self.user.is_staff:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            else:
                self.assertEqual(
                    response.status_code, status.HTTP_403_FORBIDDEN
                )

            response = self.client.delete(
                reverse(
                    "app:airport-detail",
                    kwargs={"pk": self.airport1.pk}
                )
            )
            if self.user.is_staff:
                self.assertEqual(
                    response.status_code, status.HTTP_204_NO_CONTENT
                )
            else:
                self.assertEqual(
                    response.status_code, status.HTTP_403_FORBIDDEN
                )

        self.user.is_staff = False
        self.user.save()

        try_different_action()

        self.user.is_staff = True
        self.user.save()

        try_different_action()

    @patch("app.serializers.AirportDetailSerializer.actual_weather")
    def test_get_airport_by_id(self, mock_actual_weather=None):
        mock_actual_weather.return_value = {
            "localtime": "2024-07-18 10:00",
            "temperature": "25 Celsius (feels like 27 Celsius)",
            "condition": "Sunny",
        }
        response = self.client.get(
            reverse(
                "app:airport-detail", kwargs={"pk": self.airport1.pk}
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Anaa Airport")

    def test_get_airports_by_country(self):
        response = self.client.get(
            reverse("app:airport-list") + "?country=French Polynesia"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["name"], "Anaa Airport"
        )

    def test_get_airports_by_city(self):
        response = self.client.get(reverse("app:airport-list") + "?city=Anaa")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["name"], "Anaa Airport"
        )

    def test_create_airport(self):
        url = reverse("app:airport-list")
        data = {
            "code": "CCC",
            "name": "Airport 3",
            "country": "Yemen",
            "city": "Sanaa",
            "lat": 0,
            "lon": 0
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 3)
        airport = Airport.objects.get(pk=response.data["id"])
        self.assertEqual(airport.code, "CCC")

    def test_update_airport(self):
        url = reverse(
            "app:airport-detail", kwargs={"pk": self.airport1.pk}
        )
        data = {
            "code": "DDD",
            "name": "Airport 3",
            "country": "Yemen",
            "city": "Sanaa",
            "lat": 0,
            "lon": 0
        }
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Airport.objects.count(), 2)
        airport = Airport.objects.get(pk=self.airport1.pk)
        self.assertEqual(airport.code, "DDD")

    def test_delete_airport(self):
        response = self.client.delete(
            reverse("app:airport-detail", kwargs={"pk": self.airport1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airport.objects.count(), 1)

    def test_patch_update_airport(self):
        url = reverse(
            "app:airport-detail", kwargs={"pk": self.airport1.pk}
        )
        data = {
            "code": "XXX",
        }
        response = self.client.patch(
            reverse(
                "app:airport-detail", kwargs={"pk": self.airport1.pk}
            ), data=data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Airport.objects.count(), 2)
        airport = Airport.objects.get(pk=self.airport1.pk)
        self.assertEqual(airport.code, "XXX")
