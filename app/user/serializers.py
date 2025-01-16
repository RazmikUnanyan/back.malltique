"""
Serializers for the user API view.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Метод для создания нового пользователя.
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    # Метод для обновления пользователя.
    def update(self, instance, validated_data):
        """Обновляет и возвращает пользователя."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:  # Если передан пароль:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    # Метод для валидации данных.
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Пытаемся аутентифицировать пользователя.
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:  # Если аутентификация не удалась:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
