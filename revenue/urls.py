from django.conf.urls import url

from . import views

app_name = 'revenue'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^receipt/add/(?P<lot>[\w-]+)/$', views.create_receipt, name='create-receipt'),
]
