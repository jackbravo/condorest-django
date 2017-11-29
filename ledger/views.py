from datetime import datetime

from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import MonthArchiveView
from django.db.models import Q, Sum
from django.utils.functional import cached_property

from condorest.utils import dictfetchall
from condorest.views import StaffRequiredMixin
from ledger.forms import AccountEntryForm
from ledger.models import Account, Entry


@staff_member_required
def index(request):
    from django.db import connection

    with connection.cursor() as cursor:
        sql = '''SELECT id, name, MAX(date) date, SUM(amount) amount, type FROM (
            SELECT a.id, name, MAX(date) date, SUM(amount) amount, type
            FROM ledger_entry e
            INNER JOIN ledger_account a ON e.debit_account_id = a.id
            GROUP BY a.id, name
            UNION ALL
            SELECT a.id, name, MAX(date) date, -SUM(amount) amount, type
            FROM ledger_entry e
            INNER JOIN ledger_account a ON e.credit_account_id = a.id
            GROUP BY a.id, name
        ) as ledger
        GROUP BY id, name, type
        ORDER BY type, name
        '''

        cursor.execute(sql)
        data = dictfetchall(cursor)

        previous_type = None
        types_data = []
        for row in data:
            if previous_type != row['type']:
                types_data.append({'name': row['type'], 'data':[], 'amount': Decimal('0.00')})
                previous_type = row['type']
            types_data[-1]['data'].append(row)
            types_data[-1]['amount'] += row['amount']


        return render(request, 'ledger/index.html', context={
            'data': types_data,
        })

class AccountArchiveView(StaffRequiredMixin, MonthArchiveView):
    date_field = 'date'
    month_format = '%m'
    template_name = 'ledger/account_archive.html'
    allow_future = True

    @cached_property
    def account(self):
        return get_object_or_404(Account, id=self.kwargs['account'])

    def get_queryset(self):
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

        initial = {
            'date': context['entry_list'].last().date if context['entry_list'] else datetime.now(),
        }
        context['form'] = self.get_form(initial=initial)

        return context

    def get_form(self, initial=None, data=None):
        form = AccountEntryForm(account=self.account, initial=initial, data=data)
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entry created.')
            return HttpResponseRedirect(request.get_full_path())

        # mimic get method on BaseDateListView
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        context = self.get_context_data(object_list=self.object_list,
                                        date_list=self.date_list, **kwargs)
        context.update(extra_context)
        context['form'] = form
        return self.render_to_response(context)
