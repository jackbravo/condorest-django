from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lots.models import Contact

DEBIT = 'debit'
CREDIT = 'credit'


class Account(models.Model):
    DEBIT_TYPES = (
        ('asset', 'Asset'),
        ('expense', 'Expense'),
    )
    CREDIT_TYPES = (
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
    )
    TYPES = DEBIT_TYPES + CREDIT_TYPES

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPES, db_index=True)
    contra = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Entry(models.Model):
    details = models.CharField(max_length=254, blank=True, null=True)
    date = models.DateField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    debit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='debit_entries')
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='credit_entries')
    amount = models.DecimalField(max_digits=13, decimal_places=2)

    class Meta:
        ordering = ['date', 'id']

    def clean(self):
        if self.amount == 0:
            raise ValidationError({'amount': _("Amount must not be 0")})

    def delete(self, using=None, keep_parents=False):
        if hasattr(self, 'receipt'):
            receipt = self.receipt
            receipt.save_in_ledger = False
            receipt.entry = None
            receipt.save()
        if hasattr(self, 'expensenote'):
            expensenote = self.expensenote
            expensenote.save_in_ledger = False
            expensenote.entry = None
            expensenote.save()
        super().delete(using=using, keep_parents=keep_parents)

    def details_summary(self):
        return self.details.split('\n', 1)[0]


class IncomeExpenseNote(models.Model):
    date = models.DateField(db_index=True)
    number = models.CharField(max_length=254, null=True, blank=True, db_index=True)
    details = models.CharField(max_length=254, blank=True)
    amount = models.DecimalField(max_digits=13, decimal_places=2)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, null=True, blank=True)
    save_in_ledger = models.BooleanField(blank=True, default=True)
    debit_account = models.ForeignKey(Account, related_name='debit_accounts')
    credit_account = models.ForeignKey(Account, related_name='credit_accounts')
    entry = models.OneToOneField(Entry, on_delete=models.SET_NULL, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['date', 'id']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.save_in_ledger:
            if self.entry is None:
                entry = Entry(date=self.date,
                              details=self.details,
                              amount=self.amount,
                              debit_account=self.debit_account,
                              credit_account=self.credit_account)
                entry.save()
                self.entry = entry
            else:
                self.entry.date = self.date
                self.entry.details = self.details
                self.entry.debit_account = self.debit_account
                self.entry.credit_account = self.credit_account
                self.entry.amount = self.amount
                self.entry.save()
        else:
            if self.entry is not None:
                self.entry.delete()
                self.entry = None
        super().save(force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.entry is not None:
            self.entry.delete()
        super().delete(using=using, keep_parents=keep_parents)

    def details_summary(self):
        return self.details.split('\n', 1)[0]
