from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileEditForm, CustomPasswordChangeForm
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def user_login(request):
    """Вход с восстановлением удаленных аккаунтов"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
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
                    # Обычный вход
                    login(request, user)
                    return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def confirm_restore(request):
    """Страница подтверждения восстановления"""
    user_id = request.session.get('user_to_restore_id')

    if not user_id:
        return redirect('users:login')

    try:
        user = User.objects.get(id=user_id, is_deleted=True)
    except User.DoesNotExist:
        return redirect('users:login')

    if request.method == 'POST':
        # Восстанавливаем аккаунт
        user.restore()

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
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_logout(request):
    logout(request)
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