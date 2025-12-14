from django import forms
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
            'shipping_country',
            'payment_method',
            'notes'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Иван Иванов', 'class': 'form-input'}),
            'customer_email': forms.EmailInput(attrs={'placeholder': 'ivan@example.com', 'class': 'form-input'}),
            'customer_phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67', 'class': 'form-input'}),
            'shipping_address': forms.Textarea(attrs={'placeholder': 'ул. Примерная, д. 1, кв. 1', 'rows': 3, 'class': 'form-textarea'}),
            'shipping_city': forms.TextInput(attrs={'placeholder': 'Москва', 'class': 'form-input'}),
            'shipping_zip_code': forms.TextInput(attrs={'placeholder': '123456', 'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Дополнительные пожелания к заказу...', 'rows': 3, 'class': 'form-textarea'}),
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
            'notes': 'Комментарий к заказу',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (1, '⭐'),
                (2, '⭐⭐'),
                (3, '⭐⭐⭐'),
                (4, '⭐⭐⭐⭐'),
                (5, '⭐⭐⭐⭐⭐'),
            ]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв о товаре...', 'class': 'form-textarea'}),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий'
        }