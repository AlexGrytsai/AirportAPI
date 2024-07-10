from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """

    class Meta:
        model = User
        fields = [
            "id", "email", "password", "is_staff", "first_name", "last_name"
        ]
        read_only_fields = ["is_staff", ]
        extra_kwargs = {"password": {
            "write_only": True,
            "min_length": 8,
            "max_length": 64,
            "validators": [validate_password],
            "style": {"input_type": "password", "placeholder": "Password"}
        },
            "first_name": {
                "required": False,
                "style": {
                    "input_type": "text",
                    "placeholder": "First Name (optional field)"
                }
            },
            "last_name": {
                "required": False,
                "style": {
                    "input_type": "text",
                    "placeholder": "Last Name (optional field)"
                }
            }
        }

    def create(self, validated_data: dict) -> User:
        """
        Create and return a new user instance with the validated data.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        """
       Update and return an existing user instance with the validated data.
       """
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for authenticating a user with email and password.
    """

    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        style={"input_type": "password"},
        label=_("Password"),
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate and authenticate the user with the provided email and password.
        """
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _("User account is disabled.")
                    raise serializers.ValidationError(
                        msg, code="authorization"
                    )
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(
                    msg, code="authorization"
                )
        else:
            msg = _("Must include email and password.")
            raise serializers.ValidationError(
                msg, code="authorization"
            )

        attrs["user"] = user
        return attrs
