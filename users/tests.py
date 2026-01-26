# users/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserModelTests(TestCase):
    """Тесты модели пользователя"""

    def setUp(self):
        """Создаем тестового пользователя"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('TestPass123'))
        self.assertFalse(self.user.is_deleted)
        self.assertIsNone(self.user.deleted_at)
        self.assertTrue(self.user.is_active)

    def test_user_soft_delete(self):
        """Тест мягкого удаления пользователя"""
        self.user.soft_delete()
        self.assertTrue(self.user.is_deleted)
        self.assertIsNotNone(self.user.deleted_at)
        self.assertFalse(self.user.is_active)

    def test_user_restore(self):
        """Тест восстановления пользователя"""
        self.user.soft_delete()
        self.user.restore()
        self.assertFalse(self.user.is_deleted)
        self.assertIsNone(self.user.deleted_at)
        self.assertTrue(self.user.is_active)

    def test_get_restore_days_left(self):
        """Тест расчета дней до удаления"""
        self.user.soft_delete()
        days_left = self.user.get_restore_days_left()
        self.assertGreaterEqual(days_left, 0)
        self.assertLessEqual(days_left, 30)

    def test_is_restorable(self):
        """Тест проверки возможности восстановления"""
        self.user.soft_delete()
        self.assertTrue(self.user.is_restorable())

    def test_get_years_with_us(self):
        """Тест расчета лет с нами"""
        years = self.user.get_years_with_us()
        self.assertGreaterEqual(years, 1)

    def test_superuser_creation(self):
        """Тест создания суперпользователя"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)


class UserViewsTests(TestCase):
    """Тесты представлений пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.login_url = reverse('users:login')
        self.register_url = reverse('users:register')
        self.profile_url = reverse('users:profile')
        self.logout_url = reverse('users:logout')

    def test_login_view_get(self):
        """Тест GET запроса к странице входа"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')
        self.assertContains(response, 'Войти в аккаунт')

    def test_login_view_post_success(self):
        """Тест успешного входа"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_view_post_failure(self):
        """Тест неудачного входа"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Неверное имя пользователя')

    def test_register_view_get(self):
        """Тест GET запроса к странице регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post_success(self):
        """Тест успешной регистрации"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'NewPass123',
            'password2': 'NewPass123'
        })
        self.assertEqual(response.status_code, 302)  # Редирект
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_view_authenticated(self):
        """Тест просмотра профиля авторизованным пользователем"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertContains(response, 'Привет, testuser')

    def test_profile_view_unauthenticated(self):
        """Тест просмотра профиля неавторизованным пользователем"""
        response = self.client.get(self.profile_url)
        # Должен перенаправить на страницу входа
        self.assertRedirects(response, f'/users/login/?next={self.profile_url}')

    def test_logout_view(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('home'))


class UserFormsTests(TestCase):
    """Тесты форм пользователей"""

    def test_user_creation_form_valid(self):
        """Тест валидной формы регистрации"""
        from .forms import CustomUserCreationForm

        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_creation_form_invalid(self):
        """Тест невалидной формы регистрации"""
        from .forms import CustomUserCreationForm

        # Пароли не совпадают
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'TestPass123',
            'password2': 'DifferentPass'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_profile_edit_form_valid(self):
        """Тест валидной формы редактирования профиля"""
        from .forms import ProfileEditForm

        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com'
        }
        form = ProfileEditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_edit_form_invalid_email(self):
        """Тест невалидной формы редактирования профиля (неправильный email)"""
        from .forms import ProfileEditForm

        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'invalid-email'
        }
        form = ProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class UserManagersTests(TestCase):
    """Тесты менеджеров пользователей"""

    def test_create_user(self):
        """Тест создания обычного пользователя через менеджер"""
        from .managers import CustomUserManager

        manager = CustomUserManager()
        manager.model = User

        user = manager.create_user(
            username='manageruser',
            email='manager@example.com',
            password='ManagerPass123'
        )

        self.assertEqual(user.username, 'manageruser')
        self.assertEqual(user.email, 'manager@example.com')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        """Тест создания суперпользователя через менеджер"""
        from .managers import CustomUserManager

        manager = CustomUserManager()
        manager.model = User

        user = manager.create_superuser(
            username='supermanager',
            email='super@example.com',
            password='SuperPass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_get_queryset(self):
        """Тест получения только неудаленных пользователей"""
        from .managers import CustomUserManager

        User.objects.create_user(username='user1', password='pass1')
        user2 = User.objects.create_user(username='user2', password='pass2')
        user2.soft_delete()

        manager = CustomUserManager()
        manager.model = User

        users = manager.get_queryset()
        self.assertEqual(users.count(), 1)  # Только неудаленные
        self.assertEqual(users.first().username, 'user1')