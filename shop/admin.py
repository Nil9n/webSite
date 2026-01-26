from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category', 'price')
        }),
        ('Изображение и наличие', {
            'fields': ('image', 'stock', 'available')
        }),
        ('Даты', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0  # Не показывать пустые строки для новых товаров


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created', 'status', 'payment_method', 'total_price', 'paid']
    list_filter = ['status', 'paid', 'created', 'updated', 'payment_method']
    list_editable = ['status', 'paid']  # Можно редактировать прямо в списке
    readonly_fields = ['created', 'updated']  # Эти поля только для чтения

    # Поля в форме редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'status', 'paid', 'total_price')
        }),
        ('Доставка', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_zip_code', 'shipping_country')
        }),
        ('Контактная информация', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Дополнительно', {
            'fields': ('payment_method', 'tracking_number', 'notes', 'created', 'updated')
        }),
    )

    inlines = [OrderItemInline]
    search_fields = ['id', 'user__username', 'customer_name', 'customer_email']
    date_hierarchy = 'created'


# Дополнительно: зарегистрируйте Review, если хотите
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created', 'approved']
    list_filter = ['rating', 'approved', 'created']
    list_editable = ['approved']
    search_fields = ['product__name', 'user__username', 'comment']