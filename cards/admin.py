"""Настройки панели администратора для приложения cards."""
from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    """Настройки отображения модели Card в админке."""
    list_display = ('question', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('question', 'answer')
