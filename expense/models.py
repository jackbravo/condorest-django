from django.db import models

from ledger.models import Account, IncomeExpenseNote


class ExpenseNote(IncomeExpenseNote):
    debit_account = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'type':"expense"}, related_name='expense_debit_accounts')
    credit_account = models.ForeignKey(Account, on_delete=models.CASCADE, limit_choices_to={'type':"asset"}, related_name='expense_credit_accounts')

