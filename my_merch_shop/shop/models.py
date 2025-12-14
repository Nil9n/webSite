from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def review_count(self):
        return self.reviews.count()


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f'Cart {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', '🟡 Ожидает обработки'),
        ('processing', '🟠 В обработке'),
        ('shipped', '🔵 Отправлен'),
        ('delivered', '🟢 Доставлен'),
        ('cancelled', '🔴 Отменен'),
    ]

    PAYMENT_CHOICES = [
        ('card', '💳 Банковская карта'),
        ('cash', '💵 Наличные при получении'),
        ('online', '🌐 Онлайн оплата'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    # Статус и оплата (сделаем необязательными временно)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Информация о доставке (временно необязательные)
    shipping_address = models.TextField(blank=True)  # Добавили blank=True
    shipping_city = models.CharField(max_length=100, blank=True)  # Добавили blank=True
    shipping_zip_code = models.CharField(max_length=20, blank=True)  # Добавили blank=True
    shipping_country = models.CharField(max_length=100, default='Россия')

    # Контактная информация (временно необязательные)
    customer_name = models.CharField(max_length=100, blank=True)  # Добавили blank=True
    customer_email = models.EmailField(blank=True)  # Добавили blank=True
    customer_phone = models.CharField(max_length=20, blank=True)  # Добавили blank=True

    # Комментарий к заказу
    notes = models.TextField(blank=True)

    # Трек номер для отслеживания
    tracking_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'Order {self.id} - {self.user.username}'

    def save(self, *args, **kwargs):
        # Автоматически рассчитываем общую сумму при сохранении
        if not self.total_price and hasattr(self, 'items'):
            self.total_price = sum(item.get_cost() for item in self.items.all())
        super().save(*args, **kwargs)

    def get_status_display_with_icon(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def get_payment_method_display_with_icon(self):
        return dict(self.PAYMENT_CHOICES).get(self.payment_method, self.payment_method)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_cost(self):
        return self.price * self.quantity


class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES,
                                         validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)  # Для модерации отзывов

    class Meta:
        ordering = ('-created',)
        unique_together = ['product', 'user']  # Один отзыв на товар от пользователя

    def __str__(self):
        return f'Review by {self.user.username} for {self.product.name}'

    def get_rating_stars(self):
        return '⭐' * self.rating


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']  # Уникальная пара пользователь-товар
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Дополнительная информация
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Настройки уведомлений
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    special_offers = models.BooleanField(default=True)

    # Адрес по умолчанию
    default_shipping_address = models.TextField(blank=True)
    default_city = models.CharField(max_length=100, blank=True)
    default_zip_code = models.CharField(max_length=20, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile {self.user.username}'