from django.contrib import admin
from ledger.models import Account, Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'details', 'debit_account', 'credit_account']
    list_filter = ['date', 'debit_account', 'credit_account']
    search_fields = ['details', 'debit_account__name', 'credit_account__name']
    ordering = ['-date']


admin.site.register(Entry, EntryAdmin)
admin.site.register(Account)
