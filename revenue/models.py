from django.db import models
from django.template.defaultfilters import date
from django.utils import timezone

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


class FeeLine(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    date = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)


class Fee(models.Model):
    date = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=13, decimal_places=2)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return date(self.date, "Y/m") + ' ' + self.lot.name + ' ' + str(self.amount)
