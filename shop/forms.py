from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import Order, Review
import re


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name',
            'customer_email',
            'customer_phone',
            'shipping_address',
            'shipping_city',
            'shipping_zip_code',
            'shipping_country',
            'payment_method',
            'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'placeholder': 'Иван Иванов',
                'class': 'form-input',
                'required': True,
                'pattern': '^[A-Za-zА-Яа-яЁё\\s\\-]{2,100}$',
                'title': 'ФИО должно содержать только буквы, пробелы и дефисы (2-100 символов)'
            }),
            'customer_email': forms.EmailInput(attrs={
                'placeholder': 'ivan@example.com',
                'class': 'form-input',
                'required': True,
                'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
                'title': 'Введите корректный email адрес'
            }),
            'customer_phone': forms.TextInput(attrs={
                'placeholder': '+7 (999) 123-45-67',
                'class': 'form-input',
                'required': True,
                'pattern': '^[+0-9\\s\\-\\(\\)]{10,20}$',
                'title': 'Номер телефона должен содержать от 10 до 20 цифр, может начинаться с +'
            }),
            'shipping_address': forms.Textarea(attrs={
                'placeholder': 'ул. Примерная, д. 1, кв. 1',
                'rows': 3,
                'class': 'form-textarea',
                'required': True,
                'minlength': '10',
                'maxlength': '200',
                'title': 'Адрес должен содержать от 10 до 200 символов'
            }),
            'shipping_city': forms.TextInput(attrs={
                'placeholder': 'Москва',
                'class': 'form-input',
                'required': True,
                'pattern': '^[A-Za-zА-Яа-яЁё\\s\\-\\.]{2,50}$',
                'title': 'Название города должно содержать только буквы, пробелы, точки и дефисы (2-50 символов)'
            }),
            'shipping_zip_code': forms.TextInput(attrs={
                'placeholder': '123456',
                'class': 'form-input',
                'required': True,
                'pattern': '^[0-9]{5,10}$',
                'title': 'Почтовый индекс должен содержать только цифры (5-10 символов)'
            }),
            'shipping_country': forms.TextInput(attrs={
                'placeholder': 'Россия',
                'class': 'form-input',
                'required': True,
                'pattern': '^[A-Za-zА-Яа-яЁё\\s\\-\\.]{2,50}$',
                'title': 'Название страны должно содержать только буквы, пробелы, точки и дефисы (2-50 символов)'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Дополнительные пожелания к заказу...',
                'rows': 3,
                'class': 'form-textarea',
                'maxlength': '200',
                'title': 'Максимум 200 символов'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'customer_name': 'ФИО',
            'customer_email': 'Email',
            'customer_phone': 'Телефон',
            'shipping_address': 'Адрес доставки',
            'shipping_city': 'Город',
            'shipping_zip_code': 'Почтовый индекс',
            'shipping_country': 'Страна',
            'payment_method': 'Способ оплаты',
            'notes': 'Комментарий к заказу (максимум 200 символов)',
        }

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise ValidationError("ФИО обязательно для заполнения")

        # Проверяем длину
        if len(name) < 2:
            raise ValidationError("ФИО должно содержать минимум 2 символа")
        if len(name) > 100:
            raise ValidationError("ФИО не должно превышать 100 символов")

        # Проверяем допустимые символы
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', name):
            raise ValidationError("ФИО может содержать только буквы, пробелы и дефисы")

        # Проверяем, что есть хотя бы одна буква
        if not re.search(r'[A-Za-zА-Яа-яЁё]', name):
            raise ValidationError("ФИО должно содержать хотя бы одну букву")

        return name

    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email', '').strip()
        if not email:
            raise ValidationError("Email обязателен для заполнения")

        # Проверяем базовый формат email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Введите корректный email адрес")

        if ' ' in email:
            raise ValidationError("Email не может содержать пробелы")

        return email

    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone', '').strip()
        if not phone:
            raise ValidationError("Телефон обязателен для заполнения")

        # Удаляем все нецифровые символы кроме +
        clean_phone = ''.join(c for c in phone if c.isdigit() or c == '+')

        if len(clean_phone) < 10:
            raise ValidationError("Номер телефона должен содержать минимум 10 цифр")
        if len(clean_phone) > 20:
            raise ValidationError("Номер телефона не должен превышать 20 символов")

        # Проверяем, начинается ли с + (если указан)
        if phone.startswith('+') and not phone[1:].replace(' ', '').replace('-', '').replace('(', '').replace(')',
                                                                                                              '').isdigit():
            raise ValidationError("После '+' должны идти только цифры")

        return phone

    def clean_shipping_address(self):
        address = self.cleaned_data.get('shipping_address', '').strip()
        if not address:
            raise ValidationError("Адрес обязателен для заполнения")

        if len(address) < 10:
            raise ValidationError("Адрес должен содержать минимум 10 символов")
        if len(address) > 200:
            raise ValidationError("Адрес не должен превышать 200 символов")

        return address

    def clean_shipping_city(self):
        city = self.cleaned_data.get('shipping_city', '').strip()
        if not city:
            raise ValidationError("Город обязателен для заполнения")

        if len(city) < 2:
            raise ValidationError("Название города должно содержать минимум 2 символа")
        if len(city) > 50:
            raise ValidationError("Название города не должно превышать 50 символов")

        # Проверяем допустимые символы
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-\.]+$', city):
            raise ValidationError("Название города может содержать только буквы, пробелы, точки и дефисы")

        return city

    def clean_shipping_zip_code(self):
        zip_code = self.cleaned_data.get('shipping_zip_code', '').strip()
        if not zip_code:
            raise ValidationError("Почтовый индекс обязателен для заполнения")

        # Проверяем, что только цифры
        if not zip_code.isdigit():
            raise ValidationError("Почтовый индекс должен содержать только цифры")

        # Проверяем длину
        if len(zip_code) < 5:
            raise ValidationError("Почтовый индекс должен содержать минимум 5 цифр")
        if len(zip_code) > 10:
            raise ValidationError("Почтовый индекс не должен превышать 10 цифр")

        return zip_code

    def clean_shipping_country(self):
        country = self.cleaned_data.get('shipping_country', '').strip()
        if not country:
            raise ValidationError("Страна обязательна для заполнения")

        if len(country) < 2:
            raise ValidationError("Название страны должно содержать минимум 2 символа")
        if len(country) > 50:
            raise ValidationError("Название страны не должно превышать 50 символов")

        # Проверяем допустимые символы
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-\.]+$', country):
            raise ValidationError("Название страны может содержать только буквы, пробелы, точки и дефисы")

        return country

    def clean_notes(self):
        notes = self.cleaned_data.get('notes', '').strip()

        if notes and len(notes) > 200:
            raise ValidationError("Комментарий не должен превышать 200 символов")

        return notes


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '⭐ (1 звезда)'),
        (2, '⭐⭐ (2 звезды)'),
        (3, '⭐⭐⭐ (3 звезды)'),
        (4, '⭐⭐⭐⭐ (4 звезды)'),
        (5, '⭐⭐⭐⭐⭐ (5 звезд)'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label='Оценка',
        required=True,
        error_messages={
            'required': 'Пожалуйста, выберите оценку от 1 до 5 звезд'
        }
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Напишите ваш отзыв о товаре...',
            'class': 'form-textarea',
            'minlength': '10',
            'maxlength': '1000'
        }),
        label='Комментарий',
        required=False,
        max_length=1000
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение для рейтинга, если есть
        if self.instance and self.instance.pk:
            self.fields['rating'].initial = str(self.instance.rating)

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise ValidationError("Пожалуйста, выберите оценку")
        try:
            return int(rating)
        except ValueError:
            raise ValidationError("Неверное значение оценки")

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if comment and len(comment) < 10:
            raise ValidationError("Комментарий должен содержать минимум 10 символов")
        return comment

    def save(self, commit=True):
        review = super().save(commit=False)
        if commit:
            review.save()
        return review