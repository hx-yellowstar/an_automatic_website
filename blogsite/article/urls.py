from article import views
from django.contrib import admin
from django.conf.urls import url

urlpatterns = [
    url('(.+)$', views.articlesite),
]
