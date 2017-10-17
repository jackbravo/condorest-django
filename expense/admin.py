from django.contrib import admin

from expense.models import ExpenseNote


class ExpenseNoteAdmin(admin.ModelAdmin):
    list_display = ['date', 'contact', 'account', 'amount']
    readonly_fields = ['amount']
    fields = ('date', 'contact', 'number', 'details', 'account', 'amount', 'save_in_ledger')


admin.site.register(ExpenseNote, ExpenseNoteAdmin)
