from django.shortcuts import render, get_object_or_404
from django.views.generic import MonthArchiveView

from condorest.utils import dictfetchall
from ledger.models import Account, Entry


def index(request):
    from django.db import connection

    with connection.cursor() as cursor:
        sql = '''SELECT ac.id, name, SUM(amount) amount, type
        FROM ledger_account ac
        INNER JOIN ledger_amount am ON am.account_id = ac.id
        GROUP BY ac.id, name
        ORDER BY name, type'''

        cursor.execute(sql)
        data = dictfetchall(cursor)

        return render(request, 'ledger/index.html', context={
            'data': data,
        })

class AccountArchiveView(MonthArchiveView):
    date_field = 'date'
    month_format = '%m'
    template_name = 'ledger/account_archive.html'

    def get_queryset(self):
        self.account = get_object_or_404(Account, name=self.kwargs['account'])
        return Entry.objects.filter(amount__account=self.account)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        #context['book_list'] = Book.objects.all()
        return context
