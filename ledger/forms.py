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

    def __init__(self, account, *args, **kwargs):
        self.account = account
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
