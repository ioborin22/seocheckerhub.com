from django.contrib import admin
from django.urls import path
from checker import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<path:url>/', views.index, name='url_analysis'),
    path('', views.index, name='index'),
]
