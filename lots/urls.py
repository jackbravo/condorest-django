from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search-ajax/$', views.search_ajax, name='search-ajax'),
]
