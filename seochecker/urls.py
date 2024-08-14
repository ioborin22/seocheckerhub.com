from django.contrib import admin
from django.urls import path
from checker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze/', views.url_analysis, name='url_analysis'),  # Добавлен отдельный путь для анализа
    path('', views.index, name='index'),  # Главная страница
]
