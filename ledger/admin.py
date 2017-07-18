from django.contrib import admin

from ledger.models import Amount, Account, Entry


class AmountInline(admin.TabularInline):
    model = Amount
    extra = 2


class EntryAdmin(admin.ModelAdmin):
    inlines = [AmountInline]


admin.site.register(Entry, EntryAdmin)
admin.site.register(Account)
