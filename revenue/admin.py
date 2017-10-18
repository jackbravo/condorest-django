from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _

from revenue.models import Receipt, FeeLine, Fee


class FeeLinesInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super(FeeLinesInlineFormSet, self).clean()

        total = 0
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE'):
                continue # there are other errors in the form or the item was deleted
            total += form.cleaned_data.get('amount', 0)

        self.instance.amount = total


class FeeLineForm(forms.ModelForm):
    def clean(self):
        pass


class FeeLinesInline(admin.TabularInline):
    form = FeeLineForm
    model = FeeLine
    formset = FeeLinesInlineFormSet
    extra = 1

    def get_extra (self, request, obj=None, **kwargs):
        """Don't add any extra forms if the related object already exists."""
        if obj:
            return 0
        return self.extra


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['date', 'contact', 'debit_account', 'credit_account', 'amount']
    readonly_fields = ['amount']
    fields = ('date', 'contact', 'number', 'details', 'debit_account', 'credit_account', 'amount', 'save_in_ledger')
    inlines = [FeeLinesInline]


class FeeAdmin(admin.ModelAdmin):
    list_display = ['date', 'lot', 'amount']
    list_filter = ['date']
    list_select_related = ['lot']


admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(Fee, FeeAdmin)
