from django.db import models
from django.utils import timezone

from ledger.models import Entry
from lots.models import Contact, Lot
from month.models import MonthField


class Receipt(models.Model):
    date = models.DateField(db_index=True)
    number = models.IntegerField(null=True, blank=True, db_index=True)
    details = models.CharField(max_length=254, blank=True)
    total_amount = models.DecimalField(max_digits=13, decimal_places=2)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    entry = models.ForeignKey(Entry, null=True, blank=True, on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FeeLine(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    date_start = MonthField(db_index=True, default=timezone.now)
    date_end = MonthField(db_index=True, default=timezone.now)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
