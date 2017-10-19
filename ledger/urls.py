from django.conf.urls import url

from ledger.views import AccountArchiveView
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<account>[\w-]+)/(?P<year>[0-9]{4})/(?P<month>[-\w]+)/$', AccountArchiveView.as_view(), name='account-archive'),
]
