from datetime import datetime

from decimal import Decimal
from django.shortcuts import render, get_object_or_404

from lots.models import Lot
from revenue.forms import ReceiptForm
from revenue.models import Receipt, Fee


def index(request):
    from django.db import connection

    with connection.cursor() as cursor:
        year = datetime.now().year
        sql = '''SELECT * from crosstab($$
          SELECT name, date, sum(amount) FROM (
            SELECT lot_id, date, -amount as amount
            FROM revenue_fee
            WHERE date >= '2017-01-01'::date AND date < '2018-01-01'::date
            UNION ALL
            SELECT lot_id, date, amount
            FROM revenue_feeline
            WHERE date >= '2017-01-01'::date and date < '2018-01-01'::date
          ) as fees
          INNER JOIN lots_lot ON lots_lot.id = lot_id
          GROUP BY name, date
          ORDER BY 1, 2
        $$, $$
          SELECT m::date
          FROM generate_series(timestamp '2017-01-01', timestamp '2017-12-01', '1 month') m
        $$) as (
          lot varchar,
          "jan" numeric(13,2),
          "feb" numeric(13,2),
          "mar" numeric(13,2),
          "apr" numeric(13,2),
          "may" numeric(13,2),
          "jun" numeric(13,2),
          "jul" numeric(13,2),
          "aug" numeric(13,2),
          "sep" numeric(13,2),
          "oct" numeric(13,2),
          "nov" numeric(13,2),
          "dec" numeric(13,2))'''

        cursor.execute(sql)
        data = cursor.fetchall()

        return render(request, 'revenue/index.html', context={
            'data': data,
        })

def create_receipt(request, lot):
    lot = get_object_or_404(Lot, name=lot)
    receipts = Receipt.objects.filter(contact=lot.owner).order_by('-date', '-id')
    fees = Fee.objects.filter(lot=lot)
    form = ReceiptForm()

    balance = Decimal('0.00')
    for fee in fees:
        balance += fee.amount
        fee.balance = balance

    return render(request, 'revenue/create_receipt.html', context={
        'lot': lot,
        'receipts': receipts,
        'fees': fees,
        'balance': balance,
        'form': form,
    })
