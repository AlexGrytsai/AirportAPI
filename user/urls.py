from django.urls import path

from user.views import ManageUserView
from user.views import UserView

urlpatterns = [
    path("", UserView.as_view(), name="users"),
    path("me/", ManageUserView.as_view(), name="me"),
]

app_name = "user"
