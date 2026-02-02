from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileEditForm, CustomPasswordChangeForm
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def restore_account(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        try:
            # Используем _base_manager чтобы обойти фильтрацию менеджера
            user = User._base_manager.get(
                username=username,
                email=email,
                is_deleted=True
            )

            if user.is_restorable():
                # Сохраняем в сессии для подтверждения
                request.session['user_to_restore_id'] = user.id
                return redirect('users:confirm_restore')
            else:
                messages.error(request, 'Срок восстановления аккаунта истек (30 дней).')
                return redirect('home')

        except User.DoesNotExist:
            messages.error(request, 'Аккаунт с такими данными не найден или не был удален.')

    return render(request, 'users/restore_account.html')


def user_login(request):
    """Вход с восстановлением удаленных аккаунтов"""
    if request.method == 'POST':
        # Используем стандартную форму для получения данных
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Заполните все поля')
            return render(request, 'users/login.html', {'form': AuthenticationForm()})

        try:
            # Ищем пользователя напрямую, обходя кастомный менеджер
            user = User._base_manager.get(username=username)

            # Проверяем пароль
            if user.check_password(password):
                # Пароль верный

                # Проверяем, не удален ли аккаунт
                if user.is_deleted:
                    if user.is_restorable():
                        # Сохраняем user.id в сессии для восстановления
                        request.session['user_to_restore_id'] = user.id
                        return redirect('users:confirm_restore')
                    else:
                        messages.error(request, 'Срок восстановления аккаунта истек (30 дней).')
                        return redirect('home')
                else:
                    # Обычный вход - указываем бэкенд
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    messages.success(request, f'Добро пожаловать, {user.username}!')
                    return redirect('home')
            else:
                # Неверный пароль
                messages.error(request, 'Неверное имя пользователя или пароль')

        except User.DoesNotExist:
            # Пользователь не найден
            messages.error(request, 'Неверное имя пользователя или пароль')

        # Если дошли сюда, показываем форму с ошибками
        form = AuthenticationForm(request.POST)
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def confirm_restore(request):
    """Страница подтверждения восстановления"""
    user_id = request.session.get('user_to_restore_id')

    if not user_id:
        messages.error(request, 'Сессия восстановления не найдена')
        return redirect('users:login')

    try:
        # Используем _base_manager для поиска удаленного пользователя
        user = User._base_manager.get(id=user_id, is_deleted=True)
    except User.DoesNotExist:
        messages.error(request, 'Пользователь для восстановления не найден')
        return redirect('users:login')

    if request.method == 'POST':
        # Восстанавливаем аккаунт
        user.restore()

        # Указываем бэкенд для login()
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        # Логиним пользователя
        login(request, user)

        # Очищаем сессию
        if 'user_to_restore_id' in request.session:
            del request.session['user_to_restore_id']

        messages.success(request, '🎉 Аккаунт восстановлен! Добро пожаловать обратно!')
        return redirect('users:profile')

    return render(request, 'users/confirm_restore.html', {'user': user})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Указываем бэкенд для нового пользователя
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'users/change_password.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user

        if user.check_password(password):
            # Мягкое удаление
            user.soft_delete()

            # Выходим
            logout(request)

            messages.success(request,
                             '✅ Аккаунт удален. '
                             'Для восстановления просто войдите в аккаунт в течение 30 дней.'
                             )
            return redirect('home')
        else:
            messages.error(request, 'Неверный пароль.')
            return redirect('users:profile')

    return render(request, 'users/delete_account.html')