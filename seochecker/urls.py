from django.contrib import admin
from django.urls import path
from checker import views
from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analyze/', views.url_analysis, name='url_analysis'),  # Добавлен отдельный путь для анализа
    path('', views.index, name='index'),  # Главная страница
]
