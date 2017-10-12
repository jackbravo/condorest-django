from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^bulk-create-fees$', views.BulkCreateFeesView.as_view(), name='bulk-create-fees'),
]
