from django.db import models

# Create your models here.
from django.db import models


class Card(models.Model):
    # Категории для карточек (выбор из списка)
    CATEGORY_CHOICES = [
        ('amino_acids', 'Аминокислоты'),
        ('enzymes', 'Ферменты'),
        ('metabolism', 'Метаболизм'),
        ('vitamins', 'Витамины'),
        ('other', 'Другое'),
    ]

    question = models.CharField(max_length=500, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        """Это отображается в админке и при выводе объекта"""
        return self.question[:50]