"""blogsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import blogsite
from lab import labviews
from django.contrib import admin
from articlelistpages import views
from blogsite import universalviews
from django.conf.urls import url, include


urlpatterns = [
    url('^$', views.index),
    url('^classify/(\w+)/$', views.articleclasses),
    url('article/', include('article.urls')),
    url('^about/', views.aboutpage),
    url('^lab/', labviews.worldmap),
    url(r'^search/', include('haystack.urls')),
]

handler404 = blogsite.universalviews.pagenotfound
handler500 = blogsite.universalviews.servererror