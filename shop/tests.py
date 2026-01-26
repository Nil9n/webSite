# shop/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from .forms import OrderCreateForm, ReviewForm
from decimal import Decimal

User = get_user_model()


class CategoryModelTests(TestCase):
    """Тесты модели категории"""

    def setUp(self):
        self.category = Category.objects.create(
            name='Одежда',
            slug='clothing'
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, 'Одежда')
        self.assertEqual(self.category.slug, 'clothing')
        self.assertEqual(str(self.category), 'Одежда')


class ProductModelTests(TestCase):
    """Тесты модели товара"""

    def setUp(self):
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка Nilan',
            slug='t-shirt-nilan',
            description='Крутая футболка',
            price=Decimal('1500.00'),
            category=self.category,
            available=True
        )

    def test_product_creation(self):
        """Тест создания товара"""
        self.assertEqual(self.product.name, 'Футболка Nilan')
        self.assertEqual(self.product.price, Decimal('1500.00'))
        self.assertTrue(self.product.available)
        self.assertEqual(str(self.product), 'Футболка Nilan')

    def test_average_rating_no_reviews(self):
        """Тест среднего рейтинга без отзывов"""
        self.assertEqual(self.product.average_rating(), 0)

    def test_review_count_no_reviews(self):
        """Тест количества отзывов без отзывов"""
        self.assertEqual(self.product.review_count(), 0)


class CartModelTests(TestCase):
    """Тесты модели корзины"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1000.00'),
            category=self.category,
            available=True
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        """Тест создания корзины"""
        self.assertEqual(self.cart.user.username, 'testuser')
        self.assertEqual(str(self.cart), 'Cart testuser')

    def test_cart_total_price_empty(self):
        """Тест общей суммы пустой корзины"""
        self.assertEqual(self.cart.get_total_price(), 0)

    def test_cart_total_price_with_items(self):
        """Тест общей суммы корзины с товарами"""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(self.cart.get_total_price(), Decimal('2000.00'))


class OrderModelTests(TestCase):
    """Тесты модели заказа"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1500.00'),
            category=self.category,
            available=True
        )

    def test_order_creation(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('1500.00'),
            customer_name='Иван Иванов',
            customer_email='ivan@example.com',
            shipping_address='ул. Примерная, д. 1'
        )

        self.assertEqual(order.user.username, 'customer')
        self.assertEqual(order.total_price, Decimal('1500.00'))
        self.assertEqual(order.status, 'pending')
        self.assertFalse(order.paid)
        self.assertEqual(str(order), f'Order {order.id} - customer')

    def test_order_with_items(self):
        """Тест заказа с товарами"""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('3000.00')
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )

        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().get_cost(), Decimal('3000.00'))


class ReviewModelTests(TestCase):
    """Тесты модели отзыва"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1000.00'),
            category=self.category,
            available=True
        )

    def test_review_creation(self):
        """Тест создания отзыва"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Отличный товар!'
        )

        self.assertEqual(review.product.name, 'Футболка')
        self.assertEqual(review.user.username, 'reviewer')
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.get_rating_stars(), '⭐⭐⭐⭐⭐')
        self.assertTrue(review.approved)


class ShopViewsTests(TestCase):
    """Тесты представлений магазина"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1500.00'),
            category=self.category,
            available=True
        )

        self.product_list_url = reverse('shop:product_list')
        self.product_detail_url = reverse('shop:product_detail', args=[self.product.id])
        self.cart_url = reverse('shop:cart_detail')
        self.add_to_cart_url = reverse('shop:add_to_cart', args=[self.product.id])

    def test_home_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_product_list_view(self):
        """Тест страницы списка товаров"""
        response = self.client.get(self.product_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
        self.assertContains(response, 'Футболка')

    def test_product_detail_view(self):
        """Тест страницы деталей товара"""
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')
        self.assertContains(response, 'Футболка')
        self.assertContains(response, '1500')

    def test_add_to_cart_authenticated(self):
        """Тест добавления в корзину авторизованным пользователем"""
        self.client.login(username='testuser', password='TestPass123')

        # Сначала создаем корзину
        Cart.objects.create(user=self.user)

        response = self.client.post(self.add_to_cart_url)
        self.assertRedirects(response, self.cart_url)

        # Проверяем, что товар добавлен в корзину
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().product, self.product)

    def test_add_to_cart_unauthenticated(self):
        """Тест добавления в корзину неавторизованным пользователем"""
        response = self.client.post(self.add_to_cart_url)
        self.assertRedirects(response, reverse('users:login'))

    def test_cart_view_authenticated(self):
        """Тест просмотра корзины авторизованным пользователем"""
        self.client.login(username='testuser', password='TestPass123')
        Cart.objects.create(user=self.user)

        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')

    def test_cart_view_unauthenticated(self):
        """Тест просмотра корзины неавторизованным пользователем"""
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')
        self.assertContains(response, 'Ваша корзина пуста')


class ShopFormsTests(TestCase):
    """Тесты форм магазина"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1500.00'),
            category=self.category,
            available=True
        )

    def test_order_create_form_valid(self):
        """Тест валидной формы заказа"""
        form_data = {
            'customer_name': 'Иван Иванов',
            'customer_email': 'ivan@example.com',
            'customer_phone': '+79123456789',
            'shipping_address': 'ул. Примерная, д. 1',
            'shipping_city': 'Москва',
            'shipping_zip_code': '123456',
            'shipping_country': 'Россия',
            'payment_method': 'card'
        }
        form = OrderCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_order_create_form_invalid(self):
        """Тест невалидной формы заказа"""
        # Отсутствует обязательное поле
        form_data = {
            'customer_name': '',
            'customer_email': 'ivan@example.com',
            'customer_phone': '+79123456789'
        }
        form = OrderCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('customer_name', form.errors)

    def test_review_form_valid(self):
        """Тест валидной формы отзыва"""
        form_data = {
            'rating': '5',
            'comment': 'Отличный товар, всем рекомендую!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_no_rating(self):
        """Тест невалидной формы отзыва без рейтинга"""
        form_data = {
            'rating': '',
            'comment': 'Хороший товар'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)


class IntegrationTests(TestCase):
    """Интеграционные тесты"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )
        self.category = Category.objects.create(name='Одежда', slug='clothing')
        self.product = Product.objects.create(
            name='Футболка',
            slug='t-shirt',
            description='Описание',
            price=Decimal('1500.00'),
            category=self.category,
            available=True
        )

    def test_full_order_flow(self):
        """Тест полного цикла заказа"""
        # 1. Вход пользователя
        self.client.login(username='testuser', password='TestPass123')

        # 2. Добавление товара в корзину
        cart, created = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # 3. Создание заказа
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('3000.00'),
            customer_name='Иван Иванов',
            customer_email='ivan@example.com',
            customer_phone='+79123456789',
            shipping_address='ул. Примерная, д. 1',
            shipping_city='Москва'
        )

        # 4. Добавление товаров в заказ
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=2
        )

        # Проверяем
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, Decimal('3000.00'))
        self.assertEqual(order.status, 'pending')