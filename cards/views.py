from django.shortcuts import render
from .models import Card


def index(request):
    """Главная страница"""
    total_cards = Card.objects.count()
    return render(request, 'index.html', {'total_cards': total_cards})


def card_list(request):
    """Страница со списком всех карточек"""
    cards = Card.objects.all().order_by('category', 'question')
    return render(request, 'card_list.html', {'cards': cards})


from django.shortcuts import render


