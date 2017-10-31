from django import forms
from django_select2.forms import Select2Widget

from lots.models import Contact
from revenue.models import Receipt


class ReceiptForm(forms.ModelForm):
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(),
        widget=Select2Widget
    )

    class Meta:
        model = Receipt
        fields = ('amount', 'discount', 'discount_rate',
                  'date', 'contact', 'number', 'details',
                  'debit_account', 'credit_account', 'save_in_ledger',)
        widgets = {
            'details': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        }
