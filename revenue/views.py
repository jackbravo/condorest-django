from datetime import datetime

from django.shortcuts import render


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
          GROUP BY name, date order by date
        $$, $$
          SELECT m::date
          FROM generate_series(timestamp '%s-01-01', timestamp '%s-12-01', '1 month') m
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

        cursor.execute(sql, [year, year])
        data = cursor.fetchall()

        return render(request, 'revenue/index.html', context={
            'data': data,
        })
