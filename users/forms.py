from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваше имя',
                'pattern': '.*\\S+.*',
                'title': 'Поле не может состоять только из пробелов'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите вашу фамилию',
                'pattern': '.*\\S+.*',
                'title': 'Поле не может состоять только из пробелов'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите ваш email',
                'pattern': '.*\\S+.*',
                'title': 'Поле не может состоять только из пробелов'
            }),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name or first_name == '':
            return ''  # Разрешаем пустое поле, но не пробелы
        if len(first_name) < 2:
            raise ValidationError("Имя должно содержать минимум 2 символа")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name or last_name == '':
            return ''  # Разрешаем пустое поле, но не пробелы
        if len(last_name) < 2:
            raise ValidationError("Фамилия должна содержать минимум 2 символа")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not email:
            raise ValidationError("Email обязателен для заполнения")
        if ' ' in email:
            raise ValidationError("Email не может содержать пробелы")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})