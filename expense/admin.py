from django.contrib import admin

from expense.models import ExpenseNote


class ExpenseNoteAdmin(admin.ModelAdmin):
    list_display = ['date', 'save_in_ledger', 'details', 'contact', 'credit_account', 'debit_account', 'amount']
    list_filter = ['date', 'save_in_ledger']
    fields = ('date', 'contact', 'number', 'details', 'credit_account', 'debit_account', 'amount', 'save_in_ledger')
    ordering = ['-date']


admin.site.register(ExpenseNote, ExpenseNoteAdmin)
