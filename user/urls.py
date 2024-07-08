from django.urls import path
from user.views import CreateUserView
from user.views import ManageUserView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("me/", ManageUserView.as_view(), name="me"),
]

app_name = "user"
