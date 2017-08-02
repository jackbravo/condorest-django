from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _

from ledger.models import Entry, Account
from revenue.models import Receipt, FeeLine


class FeeLinesInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super(FeeLinesInlineFormSet, self).clean()

        total = 0
        for form in self.forms:
            if not form.is_valid() or form.cleaned_data.get('DELETE'):
                continue # there are other errors in the form or the item was deleted
            total += form.cleaned_data.get('amount', 0)

        self.instance.total_amount = total


class FeeLineForm(forms.ModelForm):
    def clean(self):
        if self.cleaned_data['date_start'] > self.cleaned_data['date_end']:
            raise ValidationError(_("Date start must be before date end"))


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


class ReceiptForm(forms.ModelForm):
    save_in_ledger = forms.BooleanField(initial=True, required=False)
    asset = forms.ModelChoiceField(Account.objects.filter(type="asset"), label=_("Asset account"))


class ReceiptAdmin(admin.ModelAdmin):
    form = ReceiptForm
    readonly_fields = ['total_amount']
    fields = ('date', 'contact', 'number', 'details', 'asset', 'total_amount')
    inlines = [FeeLinesInline]

    def get_fields(self, request, obj=None):
        """Only show _save_in_ledger_ field in new forms"""
        if obj is None:
            return self.fields + ('save_in_ledger',)
        else:
            return self.fields

    def save_model(self, request, obj, form, change):
        total = obj.total_amount
        if obj.pk is None and form.cleaned_data['save_in_ledger']:
            entry = Entry(date=form.cleaned_data["date"])
            entry.save()
            revenue = Account.objects.get(name="Fees")
            entry.amount_set.create(amount=total, account=revenue)
            entry.amount_set.create(amount=-total, account=form.cleaned_data["asset"])
            obj.entry = entry
        elif obj.entry is not None:
            a1, a2 = obj.entry.amount_set.all()
            a1.amount = total
            a1.save()
            a2.amount = -total
            a2.account = form.cleaned_data["asset"]
            a2.save()
            obj.entry.date = form.cleaned_data["date"]
            obj.entry.save()
        super(ReceiptAdmin, self).save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        if obj.entry is not None:
            obj.entry.delete()
        super(ReceiptAdmin, self).delete_model(request, obj)


admin.site.register(Receipt, ReceiptAdmin)
