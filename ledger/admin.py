from django.contrib import admin
from ledger.models import Account, Entry


class EntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'details', 'debit_account', 'credit_account']
    list_filter = ['date']


admin.site.register(Entry, EntryAdmin)
admin.site.register(Account)
