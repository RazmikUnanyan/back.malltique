"""
Database models.
"""
from django.conf import settings  # Импорт настроек проекта Django.
from django.db import models  # Импортируем базовый модуль для работы с моделями.
from django.contrib.auth.models import (  # Импортируем базовые классы для работы с пользователями.
    AbstractBaseUser,  # Базовый класс для пользовательской модели.
    BaseUserManager,  # Менеджер для управления пользовательскими объектами.
    PermissionsMixin,  # Добавляет поддержку разрешений и групп.
)
from django.db.models import CharField  # Импортируем поле для текстовых данных.


class UserManager(BaseUserManager):  # Кастомный менеджер для модели пользователя.
    """Менеджер для управления пользователями."""

    def create_user(self, email, password=None, **extra_fields):
        """Создает, сохраняет и возвращает нового пользователя."""
        if not email:  # Проверяем, указан ли email.
            raise ValueError('У пользователя должен быть email.')  # Выбрасываем ошибку, если email отсутствует.
        user = self.model(email=self.normalize_email(email), **extra_fields)  # Создаем экземпляр модели с нормализованным email.
        user.set_password(password)  # Устанавливаем пароль.
        user.save(using=self._db)  # Сохраняем пользователя в базу данных.

        return user  # Возвращаем созданного пользователя.

    def create_superuser(self, email, password):
        """Создает и возвращает суперпользователя."""
        user = self.create_user(email, password)  # Создаем обычного пользователя.
        user.is_staff = True  # Делаем его сотрудником (имеющим доступ к админке).
        user.is_superuser = True  # Назначаем статус суперпользователя.
        user.save(using=self._db)  # Сохраняем изменения в базе данных.

        return user  # Возвращаем суперпользователя.


class User(AbstractBaseUser, PermissionsMixin):  # Создаем пользовательскую модель, наследуем базовый пользовательский класс.
    """Модель пользователя в системе."""
    email = models.EmailField(max_length=255, unique=True)  # Поле email, обязательное и уникальное.
    name = models.CharField(max_length=255)  # Поле имени пользователя.
    is_active = models.BooleanField(default=True)  # Статус активности пользователя.
    is_staff = models.BooleanField(default=False)  # Является ли пользователь сотрудником (доступ к админке).

    objects = UserManager()  # Подключаем кастомный менеджер пользователей.

    USERNAME_FIELD = 'email'  # Указываем, что для аутентификации используется email.


class Recipe(models.Model):  # Модель для хранения рецептов.
    """Объекты рецептов."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Связываем рецепт с пользователем через кастомную модель пользователя.
        on_delete=models.CASCADE,  # Если пользователь удален, все связанные рецепты удаляются.
    )
    title = models.CharField(max_length=100)  # Название рецепта.
    description = models.TextField(blank=True)  # Описание рецепта, необязательное поле.
    time_minutes = models.IntegerField()  # Время приготовления в минутах.
    price = models.DecimalField(max_digits=5, decimal_places=2)  # Цена рецепта, с точностью до двух знаков.
    link = models.CharField(max_length=100, blank=True)  # Ссылка на рецепт, необязательное поле.

    def __str__(self):
        """Возвращает строковое представление объекта (название рецепта)."""
        return self.title  # Выводим название рецепта.
