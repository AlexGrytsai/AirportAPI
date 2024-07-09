from django.urls import path, include
from rest_framework import routers

from app.views import AirplaneTypeViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register(
    "airplane_types", AirplaneTypeViewSet, basename="airplane-types"
)
router.register("airplanes", AirplaneViewSet, basename="airplanes")

urlpatterns = [path("", include(router.urls))]

app_name = "app"
