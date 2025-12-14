from django.apps import AppConfig

class ShopConfig(AppConfig): # <--- Название этого класса должно быть верным
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'