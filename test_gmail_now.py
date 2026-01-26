"""
Прямой тест Gmail с вашими данными
"""
import smtplib
from email.mime.text import MIMEText

# Ваши данные (уже без пробелов!)
GMAIL_USER = 'alonedance27@gmail.com'
GMAIL_PASSWORD = 'joqblzkevisvfmut'  # БЕЗ ПРОБЕЛОВ!
TO_EMAIL = 'alonedance27@gmail.com'  # Отправляем самому себе

print("=" * 60)
print("🧪 ПРЯМОЙ ТЕСТ GMAIL С ВАШИМИ ДАННЫМИ")
print("=" * 60)
print(f"Почта: {GMAIL_USER}")
print(f"Пароль: {GMAIL_PASSWORD} ({len(GMAIL_PASSWORD)} символов)")
print(f"Отправляем на: {TO_EMAIL}")
print("=" * 60)

def test_port_587():
    """Тест порта 587 с TLS"""
    print("\n1. 🔄 Тестируем порт 587 (TLS)...")
    try:
        # Создаем сообщение
        msg = MIMEText('Тест отправки Gmail через порт 587 с TLS')
        msg['Subject'] = '✅ Тест Gmail 587/TLS'
        msg['From'] = GMAIL_USER
        msg['To'] = TO_EMAIL

        # Подключаемся
        print("   Подключаемся к smtp.gmail.com:587...")
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)

        print("   Приветствие...")
        server.ehlo()

        print("   Включаем TLS...")
        server.starttls()
        server.ehlo()

        print("   Авторизуемся...")
        server.login(GMAIL_USER, GMAIL_PASSWORD)

        print("   Отправляем письмо...")
        server.send_message(msg)

        server.quit()
        print("   🎉 УСПЕХ! Письмо отправлено через порт 587")
        return True

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def test_port_465():
    """Тест порта 465 с SSL"""
    print("\n2. 🔄 Тестируем порт 465 (SSL)...")
    try:
        # Создаем сообщение
        msg = MIMEText('Тест отправки Gmail через порт 465 с SSL')
        msg['Subject'] = '✅ Тест Gmail 465/SSL'
        msg['From'] = GMAIL_USER
        msg['To'] = TO_EMAIL

        # Подключаемся
        print("   Подключаемся к smtp.gmail.com:465...")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)

        print("   Авторизуемся...")
        server.login(GMAIL_USER, GMAIL_PASSWORD)

        print("   Отправляем письмо...")
        server.send_message(msg)

        server.quit()
        print("   🎉 УСПЕХ! Письмо отправлено через порт 465")
        return True

    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False

def check_password():
    """Проверяем пароль"""
    print("\n3. 🔍 Анализ пароля...")
    password = GMAIL_PASSWORD

    print(f"   Длина: {len(password)} символов")
    print(f"   Есть пробелы: {'ДА' if ' ' in password else 'НЕТ'}")
    print(f"   Только буквы: {password.isalpha()}")

    if ' ' in password:
        print("   ⚠️  УДАЛИТЕ ПРОБЕЛЫ! Используйте: joqblzkevisvfmut")
        return False
    elif len(password) != 16:
        print("   ⚠️  Должно быть 16 символов!")
        return False

    return True

# Запускаем тесты
print("\n" + "=" * 60)
print("🚀 ЗАПУСКАЕМ ТЕСТЫ...")
print("=" * 60)

# Сначала проверяем пароль
if not check_password():
    print("\n⚠️  Исправьте пароль и перезапустите тест")
    exit(1)

# Тестируем оба порта
success_587 = test_port_587()
success_465 = test_port_465()

print("\n" + "=" * 60)
print("📊 РЕЗУЛЬТАТЫ ТЕСТОВ")
print("=" * 60)

if success_587 or success_465:
    print("🎉 УСПЕХ! Gmail работает!")
    print("\n📌 Что делать дальше:")
    print("1. Зайдите в почту alonedance27@gmail.com")
    print("2. Проверьте письма (возможно в 'Спаме')")
    print("3. Если письма пришли - всё настроено!")

    if success_587:
        print("\n✅ Используйте в settings.py:")
        print("EMAIL_PORT = 587")
        print("EMAIL_USE_TLS = True")
        print("EMAIL_USE_SSL = False")
    else:
        print("\n✅ Используйте в settings.py:")
        print("EMAIL_PORT = 465")
        print("EMAIL_USE_SSL = True")
        print("EMAIL_USE_TLS = False")

else:
    print("❌ Тесты не прошли")
    print("\n🔧 Возможные проблемы:")
    print("1. Двухфакторная аутентификация не включена")
    print("2. Пароль приложения устарел")
    print("3. Gmail блокирует 'ненадежные приложения'")
    print("\n🛠️ Решения:")
    print("1. Пересоздайте пароль приложения")
    print("2. Разрешите 'ненадежные приложения':")
    print("   https://myaccount.google.com/lesssecureapps")
    print("   (ВКЛЮЧИТЕ 'Allow less secure apps')")

print("\n" + "=" * 60)
input("Нажмите Enter для выхода...")