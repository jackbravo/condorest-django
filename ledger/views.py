from datetime import datetime

from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.views.generic import MonthArchiveView
from django.db.models import Q, Sum

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
        return Entry.objects.filter(Q(credit_account=self.account) | Q(debit_account=self.account))\
            .prefetch_related('credit_account')\
            .prefetch_related('debit_account')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['account'] = self.account

        first_day_month = datetime(year=int(self.get_year()), month=int(self.get_month()), day=1)

        debit = Entry.objects.filter(debit_account=self.account, date__lt=first_day_month).aggregate(Sum('amount'))['amount__sum']
        credit = Entry.objects.filter(credit_account=self.account, date__lt=first_day_month).aggregate(Sum('amount'))['amount__sum']
        if debit == None: debit = Decimal('0.00')
        if credit == None: credit = Decimal('0.00')
        context['previous_balance'] = debit - credit

        total_debit = Decimal('0.00')
        total_credit = Decimal('0.00')
        for entry in context['entry_list']:
            if entry.debit_account == self.account: total_debit += entry.amount
            if entry.debit_account != self.account: total_credit += entry.amount
        context['total_debit'] = total_debit
        context['total_credit'] = total_credit

        context['current_balance'] = context['previous_balance'] + (total_debit - total_credit)

        return context
