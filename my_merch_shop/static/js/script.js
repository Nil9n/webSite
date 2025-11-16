// Основные функции для сайта
document.addEventListener('DOMContentLoaded', function () {
    // Анимация появления элементов
    const animateOnScroll = function () {
        const elements = document.querySelectorAll('.product-card, .feature-card');

        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;

            if (elementPosition < screenPosition) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Инициализация анимации
    const initAnimations = function () {
        const elements = document.querySelectorAll('.product-card, .feature-card');
        elements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        });

        window.addEventListener('scroll', animateOnScroll);
        animateOnScroll(); // Первоначальный вызов
    };

    // Обработчик для кнопок корзины
    const initCartButtons = function () {
        const cartButtons = document.querySelectorAll('.btn-primary');

        cartButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                if (this.textContent.includes('корзину')) {
                    e.preventDefault();
                    addToCart(this);
                }
            });
        });
    };

    // Функция добавления в корзину (заглушка)
    function addToCart(button) {
        const productCard = button.closest('.product-card') || button.closest('.product-info');
        const productName = productCard ? productCard.querySelector('h3').textContent : 'Товар';

        // Временное уведомление
        const originalText = button.textContent;
        button.textContent = 'Добавлено!';
        button.style.background = '#27ae60';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
        }, 2000);

        console.log(`Товар "${productName}" добавлен в корзину`);
    }

    // Мобильное меню
    const initMobileMenu = function () {
        const navMenu = document.querySelector('.nav-menu');
        if (window.innerWidth <= 768) {
            // Можно добавить бургер-меню для мобильных устройств
        }
    };

    // Инициализация всех функций
    initAnimations();
    initCartButtons();
    initMobileMenu();

    // Обработчики для форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredFields = this.querySelectorAll('[required]');
            let valid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#e74c3c';
                } else {
                    field.style.borderColor = '';
                }
            });

            if (!valid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля');
            }
        });
    });
});

// Функции для работы с локальным хранилищем
const Storage = {
    set: function (key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },

    get: function (key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },

    remove: function (key) {
        localStorage.removeItem(key);
    }
};