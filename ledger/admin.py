from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from ledger.models import Amount, Account, Entry


class AmountsInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(AmountsInlineFormSet, self).clean()

        total = 0
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE'):
                return # there are other errors in the form or the item was deleted
            total += form.cleaned_data.get('amount', 0)

        if total != 0:
            raise ValidationError("All amounts must add to 0")


class AmountInline(admin.TabularInline):
    model = Amount
    formset = AmountsInlineFormSet
    extra = 2

    def get_extra (self, request, obj=None, **kwargs):
        # Don't add any extra forms if the related object already exists.
        if obj:
            return 0
        return self.extra


class EntryAdmin(admin.ModelAdmin):
    inlines = [AmountInline]
    list_display = ['date', 'details', 'created', 'updated']
    list_filter = ['date']


admin.site.register(Entry, EntryAdmin)
admin.site.register(Account)
