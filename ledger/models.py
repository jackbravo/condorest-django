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


class Amount(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=13, decimal_places=2,
                                 help_text='Record debits as positive, credits as negative')

    def clean(self):
        if self.amount == 0:
            raise ValidationError({'amount': _("Amount must not be 0")})

    @property
    def type(self):
        if self.amount.amount < 0:
            return DEBIT
        elif self.amount.amount > 0:
            return CREDIT
        else:
            # This should have been caught earlier by the database integrity check.
            # If you are seeing this then something is wrong with your DB checks.
            raise Exception('ZeroAmount error')

    def __str__(self):
        return str(self.account) + ": " + str(self.amount)


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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.save_in_ledger:
            if self.entry is None:
                entry = Entry(date=self.date, details=self.details)
                entry.save()
                entry.amount_set.create(amount=self.amount, account=self.debit_account)
                entry.amount_set.create(amount=-self.amount, account=self.credit_account)
                self.entry = entry
            else:
                a1, a2 = self.entry.amount_set.all()
                a1.amount = self.amount
                a2.account = self.debit_account
                a1.save()
                a2.amount = -self.amount
                a2.account = self.credit_account
                a2.save()
                self.entry.date = self.date
                self.entry.details = self.details
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
