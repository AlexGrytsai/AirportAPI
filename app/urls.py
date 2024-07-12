from django.urls import path, include
from rest_framework import routers

from app.views import AirplaneTypeViewSet, AirplaneViewSet, CrewViewSet, AirportViewSet, RouteViewSet

router = routers.DefaultRouter()
router.register(
    "airplane_types", AirplaneTypeViewSet, basename="airplane-types"
)
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("crews", CrewViewSet, basename="crews")
router.register("airports", AirportViewSet, basename="airports")
router.register("routes", RouteViewSet, basename="routes")

urlpatterns = [path("", include(router.urls))]

app_name = "app"
