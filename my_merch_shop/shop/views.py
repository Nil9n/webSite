from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review
from .forms import OrderCreateForm, ReviewForm


def home(request):
    products = Product.objects.filter(available=True)[:6]
    categories = Category.objects.all()

    return render(request, 'index.html', {
        'products': products,
        'categories': categories
    })


def product_list(request):
    products = Product.objects.filter(available=True)

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        current_category = Category.objects.get(slug=category_slug)
    else:
        current_category = None

    return render(request, 'shop/product_list.html', {
        'products': products,
        'categories': Category.objects.all(),
        'current_category': current_category
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    reviews = Review.objects.filter(product=product, approved=True)

    # Рассчитываем средний рейтинг
    if reviews:
        average_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        average_rating = 0

    # Проверяем, оставлял ли текущий пользователь отзыв
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'user_review': user_review
    })


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему чтобы добавлять товары в корзину')
        return redirect('users:login')

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect('shop:cart_detail')


def cart_detail(request):
    if not request.user.is_authenticated:
        return render(request, 'shop/cart.html', {'cart_empty': True})

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = sum(item.get_total_price() for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_empty': len(cart_items) == 0
    })


def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect('users:login')

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('shop:cart_detail')


def update_cart_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('users:login')

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Корзина обновлена')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')

    return redirect('shop:cart_detail')


@login_required
def order_create(request):
    """Оформление заказа"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('shop:cart_detail')

    if not cart_items:
        messages.error(request, 'Ваша корзина пуста')
        return redirect('shop:cart_detail')

    total_price = sum(item.get_total_price() for item in cart_items)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price
            order.save()

            # Создаем OrderItem'ы из CartItem'ов
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )

            # Очищаем корзину
            cart.items.all().delete()

            messages.success(request, f'Заказ #{order.id} успешно оформлен!')
            return redirect('shop:order_detail', order_id=order.id)
    else:
        # Заполняем форму данными пользователя
        initial_data = {
            'customer_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'customer_email': request.user.email,
        }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'shop/order_create.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def order_detail(request, order_id):
    """Детали заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


@login_required
def order_history(request):
    """История заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'shop/order_history.html', {'orders': orders})


# Функции для отзывов
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Проверяем, не оставлял ли пользователь уже отзыв
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if existing_review:
        messages.info(request, 'Вы уже оставляли отзыв на этот товар')
        return redirect('shop:product_detail', id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.approved = True  # Автоматически одобряем для демонстрации
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв! ✨')
            return redirect('shop:product_detail', id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'shop/add_review.html', {
        'form': form,
        'product': product
    })


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен! ✨')
            return redirect('shop:product_detail', id=review.product.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'shop/edit_review.html', {
        'form': form,
        'review': review,
        'product': review.product
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удален')
        return redirect('shop:product_detail', id=product_id)

    return render(request, 'shop/delete_review.html', {
        'review': review
    })