from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Card

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('question', 'answer')