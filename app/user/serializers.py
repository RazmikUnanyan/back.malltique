"""
Serializers for the user API view.
"""
from sys import stderr  # Импорт модуля для работы со стандартным потоком ошибок (не используется в данном коде).

from django.contrib.auth import (  # Импорт функций для работы с пользовательской моделью и аутентификацией.
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _  # Импорт функции для перевода текстов на разные языки.

from rest_framework import serializers  # Импорт модуля для создания сериализаторов в Django Rest Framework (DRF).

# Сериализатор для модели пользователя.
class UserSerializers(serializers.ModelSerializer):
    # Вложенный класс для определения метаданных сериализатора.
    class Meta:
        model = get_user_model()  # Указываем пользовательскую модель.
        fields = ['email', 'password', 'name']  # Определяем поля, которые будут сериализоваться.
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}  # Дополнительные настройки для поля "password".

    # Метод для создания нового пользователя.
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)  # Создание пользователя с использованием валидированных данных.

    # Метод для обновления пользователя.
    def update(self, instance, validated_data):
        """Обновляет и возвращает пользователя."""
        password = validated_data.pop('password', None)  # Извлекаем пароль из данных, если он присутствует.
        user = super().update(instance, validated_data)  # Обновляем остальные данные пользователя.

        if password:  # Если передан пароль:
            user.set_password(password)  # Устанавливаем новый пароль.
            user.save()  # Сохраняем изменения.

        return user  # Возвращаем обновленного пользователя.

# Сериализатор для получения токена аутентификации.
class AuthTokenSerializers(serializers.Serializer):
    email = serializers.EmailField()  # Поле для ввода email.
    password = serializers.CharField(  # Поле для ввода пароля.
        style={'input_type': 'password'},  # Указываем, что поле предназначено для пароля.
        trim_whitespace=False,  # Запрещаем автоматическое удаление пробелов.
    )

    # Метод для валидации данных.
    def validate(self, attrs):
        email = attrs.get('email')  # Получаем email из переданных данных.
        password = attrs.get('password')  # Получаем пароль.

        # Пытаемся аутентифицировать пользователя.
        user = authenticate(
            request=self.context.get('request'),  # Передаем текущий запрос.
            username=email,  # Используем email как имя пользователя.
            password=password  # Используем переданный пароль.
        )

        if not user:  # Если аутентификация не удалась:
            msg = _('Unable to authenticate with provided credentials.')  # Создаем сообщение об ошибке.
            raise serializers.ValidationError(msg, code='authorization')  # Генерируем ошибку валидации.

        attrs['user'] = user  # Добавляем пользователя в валидированные данные.
        return attrs  # Возвращаем валидированные данные.
