from article import views
from django.urls import path
from django.contrib import admin
from django.conf.urls import url

urlpatterns = [
    url('(.+)$', views.articlesite),
]
