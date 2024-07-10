from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model.

    Fields:
        id (int): The unique identifier of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
        is_staff (bool): Indicates if the user has staff privileges.

    Read-only Fields:
        is_staff (bool): Read-only field indicating staff status.

    Extra Keyword Arguments:
        password (dict): Configuration for the password field including:
            - write_only (bool): Only used for input, not serialized.
            - min_length (int): Minimum length of the password (default: 8).
            - max_length (int): Maximum length of the password (default: 64).
            - validators (list): List of validators to apply to the password.
            - style (dict): Styling options for HTML input rendering.

    Methods:
        create(validated_data: dict) -> User:
            Creates a new user object using validated data.

        update(instance: User, validated_data: dict) -> User:
            Updates an existing user object with validated data,
            including setting a new password if provided.
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

        Args:
            validated_data (dict): Validated data for creating a new user.

        Returns:
            User: Created user instance.
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        """
       Update and return an existing user instance with the validated data.

       Args:
           instance (User): Existing user instance to update.
           validated_data (dict): Validated data for updating the user.

       Returns:
           User: Updated user instance.
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

    Fields:
        email (str): The email address of the user.
        password (str): The password for the user.

    Methods:
        validate(attrs: dict) -> dict:
            Validates the provided email and password for authentication.
            Returns the validated attributes with the authenticated user.

    Raises:
        serializers.ValidationError: If authentication fails or the user
        account is disabled.
    """

    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        style={"input_type": "password"},
        label=_("Password"),
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate and authenticate the user with the provided email and password.

        Args:
            attrs (dict): The attributes containing email and password.

        Returns:
            dict: Validated attributes with the authenticated user.

        Raises:
            serializers.ValidationError: If authentication fails or the user
            is inactive.
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
