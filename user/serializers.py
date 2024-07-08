from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "is_staff"]
        read_only_fields = ["is_staff", ]
        extra_kwargs = {"password": {
            "write_only": True,
            "min_length": 8,
            "max_length": 64,
            "validators": [validate_password],
            "style": {"input_type": "password", "placeholder": "Password"}
        }
        }

    def create(self, validated_data: dict) -> User:
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        style={"input_type": "password"},
        label=_("Password"),
    )

    def validate(self, attrs: dict) -> dict:
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
