from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import Select2Widget

from ledger.models import Entry, Account


class AccountEntryForm(forms.Form):
    account = None
    date = forms.DateField()
    details = forms.CharField(max_length=254)
    transfer_to = forms.ChoiceField(widget=Select2Widget)
    debit = forms.DecimalField(max_digits=13, decimal_places=2, required=False)
    credit = forms.DecimalField(max_digits=13, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        self.fields['transfer_to'].choices = self.account_choices()

    def account_choices(self):
        accounts = Account.objects.all().order_by('type', 'name')
        if self.account:
            accounts = accounts.exclude(id=self.account.id)

        choices = [(None, '---------')]
        previous_type = None
        for account in accounts:
            if previous_type != account.type:
                choices.append((account.type, []))
                previous_type = account.type
            choices[-1][-1].append((account.id, account.name))

        return choices

    def clean(self):
        if not self.cleaned_data['debit'] and not self.cleaned_data['credit']:
            raise ValidationError(_("You need to provide either a debit or credit amount."))
        if self.cleaned_data['debit'] and self.cleaned_data['credit']:
            raise ValidationError(_("You can only provide either a debit or credit amount."))

    def save(self):
        entry = Entry(date=self.cleaned_data['date'], details=self.cleaned_data['details'])
        if self.cleaned_data['debit']:
            entry.debit_account = self.account
            entry.credit_account_id = self.cleaned_data['transfer_to']
            entry.amount = self.cleaned_data['debit']
        else:
            entry.debit_account_id = self.cleaned_data['transfer_to']
            entry.credit_account = self.account
            entry.amount = self.cleaned_data['credit']
        entry.save()
