from articlesite import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('<str:urlcode>', views.articlesite),
]
