from django.urls import path, include
from rest_framework import routers

from app.views import AirplaneViewSet, CrewViewSet, \
    AirportViewSet, FlightViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("crews", CrewViewSet, basename="crews")
router.register("airports", AirportViewSet, basename="airports")
router.register("flights", FlightViewSet, basename="flights")
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]

app_name = "app"
