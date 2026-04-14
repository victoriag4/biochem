"""Маршруты (URLs) для приложения cards."""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cards/', views.card_list, name='card-list'),
    path('cards/add/', views.card_add, name='card-add'),
    path('cards/create/', views.card_create, name='card-create'),
    path('cards/edit/<int:card_id>/', views.card_edit, name='card-edit'),
    path('cards/update/<int:card_id>/', views.card_update, name='card-update'),
    path('cards/delete/<int:card_id>/', views.card_delete, name='card-delete'),
    path('study/', views.study_mode, name='study-mode'),
    path('study/check/<int:card_id>/', views.check_answer, name='check-answer'),
    path('study/reset/', views.reset_study, name='reset-study'),
    path('stats/', views.stats, name='stats'),
]
