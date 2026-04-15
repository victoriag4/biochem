"""Views-функции для обработки запросов."""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Max
from .models import Card, StudyStats


def index(request):
    """Главная страница"""
    total_cards = Card.objects.count()  # pylint: disable=no-member
    return render(request, 'index.html', {'total_cards': total_cards})


def card_list(request):
    """Страница со списком всех карточек"""
    cards = Card.objects.all().order_by('category', 'question') # pylint: disable=no-member
    return render(request, 'card_list.html', {'cards': cards})


def card_add(request):
    """Страница с формой добавления карточки"""
    return render(request, 'card_add.html')


def card_create(request):
    """Обработка создания новой карточки (POST-запрос)"""
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        category = request.POST.get('category', 'other')
        errors = []

        # ВАЛИДАЦИЯ (проверка корректности данных)
        if not question:
            errors.append("Вопрос не может быть пустым")
        elif len(question) > 500:
            errors.append("Вопрос слишком длинный (максимум 500 символов)")

        if not answer:
            errors.append("Ответ не может быть пустым")

        # Проверка на дубликат вопроса
        if question and Card.objects.filter(question=question).exists(): # pylint: disable=no-member
            errors.append("Карточка с таким вопросом уже существует")

        if errors:
            return render(request, 'card_add.html', {
                'errors': errors,
                'question': question,
                'answer': answer,
                'category': category
            })

        # Создаём новую карточку
        Card.objects.create( # pylint: disable=no-member
            question=question,
            answer=answer,
            category=category
        )
        return redirect('card-list')

    return redirect('card-add')


def card_edit(request, card_id):
    """Страница с формой редактирования карточки"""
    card = get_object_or_404(Card, id=card_id)
    return render(request, 'card_edit.html', {'card': card})


def card_update(request, card_id):
    """Обработка обновления карточки (POST-запрос)"""
    card = get_object_or_404(Card, id=card_id)

    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        category = request.POST.get('category', 'other')
        errors = []

        if not question:
            errors.append("Вопрос не может быть пустым")
        if not answer:
            errors.append("Ответ не может быть пустым")

        # Проверка на дубликат (исключая текущую карточку)
        if (question and Card.objects.filter(question=question) # pylint: disable=no-member
                .exclude(id=card_id).exists()):
            errors.append("Карточка с таким вопросом уже существует")

        if errors:
            return render(request, 'card_edit.html', {
                'card': card,
                'errors': errors
            })

        card.question = question
        card.answer = answer
        card.category = category
        card.save()

    return redirect('card-list')


def card_delete(request, card_id):
    """Удаление карточки"""
    card = get_object_or_404(Card, id=card_id)
    if request.method == 'POST':
        card.delete()
    return redirect('card-list')


def study_mode(request):
    """Режим тренировки — показываем карточки по одной"""
    all_cards = list(Card.objects.all()) # pylint: disable=no-member

    if not all_cards:
        return redirect('card-add')

    # Инициализируем прогресс в сессии
    if 'current_card_index' not in request.session:
        request.session['current_card_index'] = 0
        request.session['streak'] = 0
        request.session['correct_total'] = 0
        request.session['incorrect_total'] = 0
        request.session['max_streak'] = 0

    current_index = request.session.get('current_card_index', 0)
    current_streak = request.session.get('streak', 0)
    max_streak = request.session.get('max_streak', 0)

    # Если прошли все карточки
    if current_index >= len(all_cards):
        # Сохраняем статистику в БД
        StudyStats.objects.create( # pylint: disable=no-member
            cards_reviewed=len(all_cards),
            correct_answers=request.session.get('correct_total', 0),
            max_streak=request.session.get('max_streak', 0)
        )

        return render(request, 'study_complete.html', {
            'total': len(all_cards),
            'correct': request.session.get('correct_total', 0),
            'streak': max_streak
        })

    current_card = all_cards[current_index]
    return render(request, 'study_mode.html', {
        'card': current_card,
        'card_number': current_index + 1,
        'total_cards': len(all_cards),
        'streak': current_streak
    })

def check_answer(request, card_id):
    """Проверка ответа пользователя"""
    card = get_object_or_404(Card, id=card_id)
    user_answer = request.POST.get('user_answer', '').strip().lower()
    correct_answer = card.answer.lower()

    # Сравниваем ответы
    is_correct = user_answer == correct_answer

    # Обновляем статистику в сессии
    if is_correct:
        request.session['streak_count'] = request.session.get('streak_count', 0) + 1
        request.session['correct_total'] = request.session.get('correct_total', 0) + 1

        # Обновляем максимальную серию
        current_streak = request.session['streak_count']
        if current_streak > request.session.get('max_streak', 0):
            request.session['max_streak'] = current_streak
    else:
        request.session['streak_count'] = 0
        request.session['incorrect_total'] = request.session.get('incorrect_total', 0) + 1

    # Переходим к следующей карточке
    request.session['current_card_index'] = request.session.get('current_card_index', 0) + 1
    request.session.modified = True

    return render(request, 'answer_feedback.html', {
        'is_correct': is_correct,
        'correct_answer': card.answer,
        'user_answer': request.POST.get('user_answer', ''),
        'streak_count': request.session.get('streak_count', 0)
    })

def reset_study(request):
    """Сброс прогресса тренировки"""
    request.session.flush()  # Очищаем всю сессию
    return redirect('study-mode')


def stats(request):
    """Страница статистики"""

    # Статистика по карточкам
    total_cards = Card.objects.count() # pylint: disable=no-member

    # Подсчёт по категориям
    categories = {}
    for cat_choice in Card._meta.get_field('category').choices: # pylint: disable=no-member,protected-access
        cat_value = cat_choice[0]
        cat_name = cat_choice[1]
        cat_count = Card.objects.filter( # pylint: disable=no-member
            category=cat_value
        ).count() # pylint: disable=no-member
        if cat_count > 0:
            categories[cat_name] = cat_count

    # Статистика по тренировкам
    study_stats = StudyStats.objects.all() # pylint: disable=no-member
    total_sessions = study_stats.count()

    if total_sessions > 0:
        # Общее количество правильных ответов
        total_correct = study_stats.aggregate(Sum('correct_answers'))['correct_answers__sum'] or 0
        total_cards_reviewed = (
            study_stats.aggregate(Sum('cards_reviewed'))['cards_reviewed__sum'] or 1
        )
        avg_accuracy = (total_correct / total_cards_reviewed) * 100

        best_streak = study_stats.aggregate(Max('max_streak'))['max_streak__max'] or 0
        recent_stats = study_stats[:10]  # последние 10 тренировок
    else:
        avg_accuracy = 0
        best_streak = 0
        recent_stats = []

    return render(request, 'stats.html', {
        'total_cards': total_cards,
        'categories': categories,
        'total_sessions': total_sessions,
        'avg_accuracy': avg_accuracy,
        'best_streak': best_streak,
        'recent_stats': recent_stats,
    })
