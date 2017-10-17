from django.db import models

from ledger.models import Account, IncomeExpenseNote


class ExpenseNote(IncomeExpenseNote):
    account = models.ForeignKey(Account, limit_choices_to={'type':"liability"})
    default_account = 'Accrued Expenses'

