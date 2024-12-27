"""
Test for models.
"""
from decimal import Decimal

from django.test import TestCase  # Импортируем базовый класс для создания тестов.
from django.contrib.auth import get_user_model  # Получаем модель пользователя, используемую в проекте.

from core import models  # Импортируем модели из приложения core.


class TestModels(TestCase):  # Создаем класс тестов, наследуемый от TestCase.
    """Тесты для моделей."""

    def test_email_user_with_successfull(self):
        """Тест: успешное создание пользователя с email."""
        email = "test@example.com"  # Тестовый email.
        password = "testpass11!"  # Тестовый пароль.
        user = get_user_model().objects.create_user(  # Создаем пользователя с указанным email и паролем.
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)  # Проверяем, что email пользователя совпадает с указанным.
        self.assertTrue(user.check_password(password))  # Проверяем, что пароль установлен правильно.

    def test_new_user_email_normalize(self):
        """Тест: email приводится к нормализованному виду при создании пользователя."""
        sample_emails = [  # Примеры email для тестирования нормализации.
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:  # Для каждого примера проверяем нормализацию.
            user = get_user_model().objects.create_user(email, 'sample123')  # Создаем пользователя.
            self.assertEqual(user.email, expected)  # Проверяем, что email нормализован правильно.

    def test_new_user_without_email_raises_error(self):
        """Тест: создание пользователя без email вызывает ошибку ValueError."""
        with self.assertRaises(ValueError):  # Ожидаем, что при отсутствии email будет вызвана ошибка.
            get_user_model().objects.create_user('', 'sample123')  # Пытаемся создать пользователя без email.

    def test_creating_superuser(self):
        """Тест: успешное создание суперпользователя."""
        user = get_user_model().objects.create_superuser(  # Создаем суперпользователя.
            'test4@example.com',
            '123'
        )

        self.assertTrue(user.is_superuser)  # Проверяем, что пользователь является суперпользователем.
        self.assertTrue(user.is_staff)  # Проверяем, что пользователь имеет статус сотрудника.

    def test_create_product(self):
        """Тест: успешное создание рецепта."""
        user = get_user_model().objects.create_user(  # Создаем пользователя для рецепта.
            'test@example.com',
            'pass123',
        )

        product = models.Product.objects.create(  # Создаем объект рецепта с указанными параметрами.
            user=user,
            title='simple product name',  # Название рецепта.
            description='simple test',  # Описание рецепта.
            price=Decimal('5.5'),  # Цена рецепта.
            time_minutes=5,  # Время приготовления в минутах.
            link="////"
        )

        self.assertEqual(str(product), product.title)  # Проверяем, что строковое представление рецепта соответствует его названию.
