from django import forms

from revenue.models import Receipt


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ('date', 'contact', 'number', 'details', 'debit_account', 'credit_account', 'amount', 'save_in_ledger')
        widgets = {
            'details': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        }
