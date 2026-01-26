from django import forms
from django.core.exceptions import ValidationError
from .models import Order, Review


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
            'shipping_country',  # ДОБАВЛЕНО
            'payment_method',
            'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'placeholder': 'Иван Иванов',
                'class': 'form-input',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'placeholder': 'ivan@example.com',
                'class': 'form-input',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'placeholder': '+7 (999) 123-45-67',
                'class': 'form-input',
                'required': True
            }),
            'shipping_address': forms.Textarea(attrs={
                'placeholder': 'ул. Примерная, д. 1, кв. 1',
                'rows': 3,
                'class': 'form-textarea',
                'required': True
            }),
            'shipping_city': forms.TextInput(attrs={
                'placeholder': 'Москва',
                'class': 'form-input',
                'required': True
            }),
            'shipping_zip_code': forms.TextInput(attrs={
                'placeholder': '123456',
                'class': 'form-input',
                'required': True
            }),
            'shipping_country': forms.TextInput(attrs={  # ДОБАВЛЕНО
                'placeholder': 'Россия',
                'class': 'form-input',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Дополнительные пожелания к заказу...',
                'rows': 3,
                'class': 'form-textarea'
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
            'shipping_country': 'Страна',  # ДОБАВЛЕНО
            'payment_method': 'Способ оплаты',
            'notes': 'Комментарий к заказу',
        }

    def clean_customer_name(self):
        name = self.cleaned_data.get('customer_name', '').strip()
        if not name:
            raise ValidationError("ФИО обязательно для заполнения")
        if len(name) < 2:
            raise ValidationError("ФИО должно содержать минимум 2 символа")
        return name

    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email', '').strip()
        if not email:
            raise ValidationError("Email обязателен для заполнения")
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
            raise ValidationError("Номер телефона слишком короткий")
        return phone


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
            'class': 'form-textarea'
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