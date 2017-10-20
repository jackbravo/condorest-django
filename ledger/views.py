from django.shortcuts import render, get_object_or_404
from django.views.generic import MonthArchiveView
from django.db.models import Q

from condorest.utils import dictfetchall
from ledger.models import Account, Entry


def index(request):
    from django.db import connection

    with connection.cursor() as cursor:
        sql = '''SELECT id, name, SUM(amount) amount, type FROM (
            SELECT a.id, name, SUM(amount) amount, type
            FROM ledger_entry e
            INNER JOIN ledger_account a ON e.debit_account_id = a.id
            GROUP BY a.id, name
            UNION ALL
            SELECT a.id, name, -SUM(amount) amount, type
            FROM ledger_entry e
            INNER JOIN ledger_account a ON e.credit_account_id = a.id
            GROUP BY a.id, name
        ) as ledger
        GROUP BY id, name, type
        ORDER BY type, name
        '''

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
        return Entry.objects.filter(Q(credit_account=self.account) | Q(debit_account=self.account))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['account'] = self.account
        return context
