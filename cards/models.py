"""Модели данных для приложения карточек биохимии."""
from django.db import models


class Card(models.Model):
    """Модель карточки с вопросом и ответом по биохимии."""
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


class StudyStats(models.Model):
    """Модель статистики тренировок пользователя."""

    date = models.DateField(auto_now_add=True, verbose_name="Дата")
    cards_reviewed = models.IntegerField(default=0, verbose_name="Просмотрено карточек")
    correct_answers = models.IntegerField(default=0, verbose_name="Правильных ответов")
    max_streak = models.IntegerField(default=0, verbose_name="Максимальная серия")

    class Meta:
        """Метаданные модели StudyStats."""
        verbose_name = "Статистика тренировки"
        verbose_name_plural = "Статистика тренировок"
        ordering = ['-date']

    def __str__(self):
        """Возвращает строковое представление статистики."""
        return f"{self.date} - {self.cards_reviewed} карточек"

    def get_accuracy(self):
        """Возвращает точность ответов в процентах."""
        if self.cards_reviewed == 0:
            return 0
        return round((self.correct_answers / self.cards_reviewed) * 100, 1)
