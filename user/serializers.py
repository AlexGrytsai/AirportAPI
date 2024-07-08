from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

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
