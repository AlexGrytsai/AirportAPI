from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError, ErrorDetail

from app.models import (
    Airplane,
    AirplaneType,
    Crew,
    Airport,
    Route,
    Flight,
    Order,
    Ticket
)
from user.models import User


class AirplaneTypeModelTest(TestCase):
    def test_str_representation(self):
        airplane_type = AirplaneType(name="Test Type")
        self.assertEqual(str(airplane_type), "Test Type")


class AirplaneModelTest(TestCase):
    def test_total_seats_calculation(self):
        airplane = Airplane(
            name="Test Airplane", code="ABC123", rows=5, seats_in_row=4
        )

        self.assertEqual(airplane.total_seats, 20)

    def test_str_representation(self):
        airplane_type = AirplaneType(name="Test Type")
        airplane = Airplane(
            name="Test Airplane",
            code="ABC123",
            rows=5,
            seats_in_row=4,
            airplane_type=airplane_type
        )

        self.assertEqual(
            str(airplane), "Test Airplane (total seats: 20)"
        )


class CrewModelTest(TestCase):

    def setUp(self):
        self.crew = Crew.objects.create(
            first_name="John",
            last_name="Doe",
            title="Captain"
        )

    def test_create_crew_instance(self):
        self.assertEqual(self.crew.first_name, "John")
        self.assertEqual(self.crew.last_name, "Doe")
        self.assertEqual(self.crew.title, "Captain")

    def test_full_name_property(self):
        self.assertEqual(self.crew.full_name, "John Doe")

    def test_str_method(self):
        self.assertEqual(str(self.crew), "John Doe (Captain)")


class AirportModelTestCase(TestCase):

    def setUp(self):
        self.airport = Airport.objects.create(
            code="AAA",
            name="Anaa Airport",
            country="French Polynesia",
            city="Anaa",
            lat=-17.3595,
            lon=-145.494
        )

    def test_code_contains_only_letters(self):
        self.assertTrue(
            self.airport.code.isalpha(), "Code must contain only letters"
        )

    def test_code_is_uppercase(self):
        self.assertTrue(
            self.airport.code.isupper(), "Code must be uppercase"
        )

    def test_country_required(self):
        self.airport.country = None
        with self.assertRaises(ValidationError):
            self.airport.full_clean()

    def test_country_exists(self):
        self.airport.country = "Test Country"
        with self.assertRaises(ValidationError):
            self.airport.full_clean()

    def test_str_method(self):
        self.assertEqual(
            str(self.airport), "Anaa Airport (Anaa | French Polynesia)"
        )


class RouteModelTest(TestCase):
    def setUp(self):
        self.source_airport = Airport.objects.create(
            code="AAA",
            name="Anaa Airport",
            country="French Polynesia",
            city="Anaa",
            lat=-17.3595,
            lon=-145.494
        )
        self.destination_airport = Airport.objects.create(
            code="AAL",
            name="Aalborg Airport",
            city="Norresundby",
            state="Nordjylland",
            country="Denmark",
            lat=57.0952,
            lon=9.85606
        )
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport
        )

    def test_route_str_method(self):
        self.assertEqual(
            self.route.__str__(),
            "Anaa Airport -> Aalborg Airport (15142 km)"
        )

    def test_clean_method_same_source_and_destination(self):
        route = Route(source=self.source_airport,
                      destination=self.source_airport)
        with self.assertRaises(ValidationError):
            route.clean()

    def test_distance_property_calculation(self):
        self.assertEqual(self.route.distance, 15142)


class FlightTestCase(TestCase):
    def setUp(self):
        self.source_airport = Airport.objects.create(
            code="AAA",
            name="Anaa Airport",
            country="French Polynesia",
            city="Anaa",
            lat=-17.3595,
            lon=-145.494
        )
        self.destination_airport = Airport.objects.create(
            code="AAL",
            name="Aalborg Airport",
            city="Norresundby",
            state="Nordjylland",
            country="Denmark",
            lat=57.0952,
            lon=9.85606
        )
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport
        )
        self.airplane_type = AirplaneType.objects.create(name="Test Type")
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            code="ABC123",
            rows=5,
            seats_in_row=4,
            airplane_type=self.airplane_type
        )
        self.capitain = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )

        self.departure_time = timezone.now()
        self.arrival_time = self.departure_time + timezone.timedelta(hours=2)

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time
        )
        self.flight.crew.set([self.capitain])

    def test_str_method(self):
        self.assertEqual(
            str(self.flight),
            f"Anaa Airport -> Aalborg Airport (ABC123,"
            f" {self.departure_time})")

    def test_clean_method_departure_time_in_past(self):
        self.departure_time = timezone.now() - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            self.flight.clean()
        self.assertEqual(
            str(cm.exception),
            "[ErrorDetail(string='Departure time cannot be in the past',"
            " code='invalid')]")

    def test_clean_method_arrival_time_before_departure_time(self):
        self.arrival_time = self.departure_time - timezone.timedelta(hours=1)
        with self.assertRaises(ValidationError) as cm:
            self.flight.clean()
        self.assertEqual(
            str(cm.exception),
            "["
            "ErrorDetail(string='Departure time cannot be in the past', "
            "code='invalid')"
            "]"
        )

    def test_clean_method_arrival_time_in_past(self):
        self.arrival_time = timezone.now() - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            self.flight.clean()
        self.assertEqual(
            str(cm.exception),
            "[ErrorDetail(string='Departure time cannot be in the past', "
            "code='invalid')]"
        )


class OrderTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpassword"
        )

        self.order = Order.objects.create(user=self.user)
        self.order_2 = Order.objects.create(user=self.user)

    def test_order_string_representation(self):
        self.assertEqual(
            str(self.order),
            f"Order #{self.order.id} by {self.user} "
            f"({self.order.created_at})"
        )


class TicketTestCase(TestCase):

    def setUp(self):
        self.source_airport = Airport.objects.create(
            code="AAA",
            name="Anaa Airport",
            country="French Polynesia",
            city="Anaa",
            lat=-17.3595,
            lon=-145.494
        )
        self.destination_airport = Airport.objects.create(
            code="AAL",
            name="Aalborg Airport",
            city="Norresundby",
            state="Nordjylland",
            country="Denmark",
            lat=57.0952,
            lon=9.85606
        )
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport
        )
        self.airplane_type = AirplaneType.objects.create(name="Test Type")
        self.airplane = Airplane.objects.create(
            name="Test Airplane",
            code="ABC123",
            rows=5,
            seats_in_row=4,
            airplane_type=self.airplane_type
        )
        self.capitain = Crew.objects.create(
            first_name="John",
            last_name="Doe",
        )

        self.departure_time = timezone.now()
        self.arrival_time = self.departure_time + timezone.timedelta(hours=2)

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=self.departure_time,
            arrival_time=self.arrival_time
        )
        self.flight.crew.set([self.capitain])
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password"
        )
        self.order = Order.objects.create(user=self.user)

    def test_validate_ticket_valid(self):
        Ticket.validate_ticket(1, 1, self.airplane, ValidationError)

    def test_validate_ticket_invalid_row(self):
        with self.assertRaises(ValidationError) as context:
            Ticket.validate_ticket(
                0, 1, self.airplane, ValidationError
            )
        self.assertEqual(
            context.exception.args[0],
            {
                "row":
                    ErrorDetail(
                        string="row number must be in available range: "
                               "(1, rows): (1, 5)",
                        code="invalid"
                    )
            }
        )

    def test_validate_ticket_invalid_seat(self):
        with self.assertRaises(ValidationError) as context:
            Ticket.validate_ticket(
                1, 0, self.airplane, ValidationError
            )
        self.assertEqual(
            context.exception.args[0],
            {
                "seat":
                    "seat number must be in available range: "
                    "(1, seats_in_row): (1, 4)"
            },
        )

    def test_clean_valid(self):
        ticket = Ticket(
            flight=self.flight,
            order=self.order,
            row=1,
            seat=1,
        )
        ticket.clean()

    def test_clean_invalid(self):
        ticket = Ticket(
            flight=self.flight,
            order=self.order,
            row=0,
            seat=1,
        )
        with self.assertRaises(ValidationError) as context:
            ticket.clean()
        self.assertEqual(
            context.exception.args[0],
            {
                "row": "row number must be in available range: "
                       "(1, rows): (1, 5)"
            },
        )

    def test_save_valid(self):
        ticket = Ticket(
            flight=self.flight,
            order=self.order,
            row=1,
            seat=1,
        )
        ticket.save()

    def test_save_invalid(self):
        ticket = Ticket(
            flight=self.flight,
            order=self.order,
            row=0,
            seat=1,
        )
        with self.assertRaises(ValidationError) as context:
            ticket.save()
        self.assertEqual(
            context.exception.args[0],
            {
                "row": "row number must be in available range: "
                       "(1, rows): (1, 5)"
            },
        )
