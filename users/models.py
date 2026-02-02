from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # Только два поля нужно
    is_deleted = models.BooleanField(default=False, verbose_name='Удален')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        """Восстанавливаем"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True  # ⬅️ ВАЖНО: теперь можно войти!
        self.save()

    def get_restore_days_left(self):
        """Дней до окончательного удаления"""
        if not self.is_deleted or not self.deleted_at:
            return 30

        deadline = self.deleted_at + timedelta(days=30)
        days_left = (deadline - timezone.now()).days
        return max(0, days_left)

    def is_restorable(self):
        """Можно ли восстановить"""
        return self.is_deleted and self.get_restore_days_left() > 0

    def get_years_with_us(self):
        """Возвращает сколько лет пользователь с нами"""
        years = timezone.now().year - self.date_joined.year
        return max(1, years)  # Минимум 1 год

    def get_cart(self):
        """Возвращает корзину пользователя, создает если нет"""
        from shop.models import Cart
        cart, created = Cart.objects.get_or_create(user=self)
        return cart