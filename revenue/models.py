from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import date
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import intcomma

from ledger.models import Entry, Account, IncomeExpenseNote
from lots.models import Contact, Lot
from month.models import MonthField
from django.utils.translation import ugettext_lazy as _


class Receipt(IncomeExpenseNote):
    debit_account = models.ForeignKey(Account, limit_choices_to={'type':"asset"}, related_name='receipt_debit_accounts')
    credit_account = models.ForeignKey(Account, limit_choices_to={'type':"revenue"},
        related_name='receipt_credit_accounts',
        default=3 # lambda: Account.objects.get(name='Fees')
    )
    discount = models.DecimalField(blank=True, max_digits=13, decimal_places=2)
    discount_rate = models.IntegerField(blank=True)

    def clean(self):
        if self.discount and self.discount_rate:
            raise ValidationError(_('Use only discount amount or discount rate, not both.'))

    def delete(self, using=None, keep_parents=False):
        new_fees = []
        for fee_line in self.feeline_set.all():
            fee = Fee.objects.filter(lot=fee_line.lot, date=fee_line.date).first()
            if fee:
                fee.amount += fee_line.amount + fee_line.discount
                fee.save()
            else:
                new_fees.append(Fee(date=fee_line.date, lot=fee_line.lot, amount=fee_line.amount + fee_line.discount))
        Fee.objects.bulk_create(new_fees)
        super().delete(using=None, keep_parents=keep_parents)

    def discount_str(self):
        if self.discount:
            return "-" + intcomma(self.discount)
        elif self.discount_rate:
            return self.discount_rate + "%"
        else:
            return ""


class FeeLine(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    discount = models.DecimalField(max_digits=13, decimal_places=2, default=Decimal('0.00'))
    date = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)

    def __str__(self):
        return date(self.date, "Y/m") + ' ' + self.lot.name + ' ' + str(self.amount)


class Fee(models.Model):
    date = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=13, decimal_places=2)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return date(self.date, "Y/m") + ' ' + self.lot.name + ' ' + str(self.amount)

    @staticmethod
    def create_fees(ids, start_date, end_date):
        from django.db import connection
        with connection.cursor() as cursor:
            sql = '''INSERT INTO revenue_fee ("date", amount, lot_id)
              SELECT t::date, default_fee, id
              FROM lots_lot
              CROSS JOIN generate_series(timestamp %s, timestamp %s, '1 month') t
              WHERE id IN %s
            '''

            cursor.execute(sql, [start_date, end_date, ids])
            return cursor.rowcount
