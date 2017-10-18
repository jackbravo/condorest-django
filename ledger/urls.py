from django.conf.urls import url

from ledger.views import AccountDetailView
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pk>[0-9]+)$', AccountDetailView.as_view(), name='account-detail'),
]
