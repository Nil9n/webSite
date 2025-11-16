from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/', views.category_list, name='category_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
]