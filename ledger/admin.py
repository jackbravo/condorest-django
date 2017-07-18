from django.contrib import admin

from ledger.models import Amount, Account, Entry


class AmountInline(admin.TabularInline):
    model = Amount
    extra = 2

    def get_extra (self, request, obj=None, **kwargs):
        # Don't add any extra forms if the related object already exists.
        if obj:
            return 0
        return self.extra


class EntryAdmin(admin.ModelAdmin):
    inlines = [AmountInline]


admin.site.register(Entry, EntryAdmin)
admin.site.register(Account)
