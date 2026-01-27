from django.contrib.auth.models import BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def get_queryset(self):
        """По умолчанию показываем только неудаленных пользователей"""
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """Все пользователи, включая удаленных"""
        return super().get_queryset()

    def only_deleted(self):
        """Только удаленные пользователи"""
        return super().get_queryset().filter(is_deleted=True)

    def restore(self, *args, **kwargs):
        """Восстановить пользователя"""
        qs = self.only_deleted().filter(*args, **kwargs)
        for user in qs:
            user.restore()

    # ДОБАВЬТЕ ЭТОТ МЕТОД для работы аутентификации
    def get_by_natural_key(self, username):
        """Для поиска при аутентификации - ищем даже удаленных"""
        return self.all_with_deleted().get(username=username)