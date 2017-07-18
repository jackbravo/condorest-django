from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    description = models.TextField(blank=True, null=True)
    date = models.DateField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Amount(models.Model):
    entry = models.ForeignKey(Entry)
    account = models.ForeignKey(Account)
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
