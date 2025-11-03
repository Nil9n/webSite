from django.contrib import admin
from django.urls import path
from django.shortcuts import render

# Просто функция которая показывает твой HTML файл
def home_page(request):
    return render(request, 'index.html')  # если главный файл называется index.html

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_page),  # главная страница
]