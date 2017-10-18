from django.contrib import admin

from expense.models import ExpenseNote


class ExpenseNoteAdmin(admin.ModelAdmin):
    list_display = ['date', 'contact', 'credit_account', 'debit_account', 'amount']
    readonly_fields = ['amount']
    fields = ('date', 'contact', 'number', 'details', 'credit_account', 'debit_account', 'amount', 'save_in_ledger')


admin.site.register(ExpenseNote, ExpenseNoteAdmin)
