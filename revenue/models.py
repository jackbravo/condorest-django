from django.db import models
from django.utils import timezone

from ledger.models import Entry, Account
from lots.models import Contact, Lot
from month.models import MonthField
from django.utils.translation import ugettext_lazy as _


class Receipt(models.Model):
    date = models.DateField(db_index=True)
    number = models.IntegerField(null=True, blank=True, db_index=True)
    details = models.CharField(max_length=254, blank=True)
    total_amount = models.DecimalField(max_digits=13, decimal_places=2)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    save_in_ledger = models.BooleanField(blank=True, default=True)
    asset = models.ForeignKey(Account, limit_choices_to={'type':"asset"})
    entry = models.ForeignKey(Entry, null=True, blank=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.save_in_ledger:
            if self.entry is None:
                entry = Entry(date=self.date)
                entry.save()
                revenue = Account.objects.get(name="Fees")
                entry.amount_set.create(amount=self.total_amount, account=revenue)
                entry.amount_set.create(amount=-self.total_amount, account=self.asset)
                self.entry = entry
            else:
                a1, a2 = self.entry.amount_set.all()
                a1.amount = self.total_amount
                a1.save()
                a2.amount = -self.total_amount
                a2.account = self.asset
                a2.save()
                self.entry.date = self.date
                self.entry.save()
        else:
            if self.entry is not None:
                self.entry.delete()
                self.entry = None
        super(Receipt, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                  update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.entry is not None:
            self.entry.delete()
        super(Receipt, self).delete(using=using, keep_parents=keep_parents)


class FeeLine(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    date_start = MonthField(db_index=True, default=timezone.now)
    date_end = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
