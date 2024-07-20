from django.urls import path, include
from rest_framework import routers

from app.views import (
    AirplaneViewSet,
    CrewViewSet,
    AirportViewSet,
    FlightViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "app"
