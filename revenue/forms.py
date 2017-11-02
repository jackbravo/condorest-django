from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import Select2Widget
from django.utils.translation import ugettext_lazy as _

from lots.models import Contact
from revenue.models import Receipt, FeeLine


class ReceiptForm(forms.ModelForm):
    lot = None
    fees = None
    balance = None

    fees_to_delete = []
    fees_to_update = []
    fee_lines = []

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

    def __init__(self, data=None, initial=None,
                 lot=None, balance=None, fees=None):
        """
        If setting lots and fees during __init__ we can create FeeLines attached to this lot.
        If setting the balance, we can provide an additional check during clean().
        """
        self.lot = lot
        self.fees = fees
        self.balance = balance
        super().__init__(data, initial=initial)

    def clean(self):
        if self.balance and self.balance < self.cleaned_data['amount']:
            raise ValidationError({'amount': _("Amount must not be greater than the balance.")})

        # this block of code appears also in create_receipt.js
        if self.fees:
            available_amount = self.cleaned_data['amount']
            available_discount = self.cleaned_data['discount']
            calculated_amount = Decimal('0.00')
            for fee in self.fees:
                month_amount = fee.amount
                month_discount = Decimal('0.00')

                # apply discount
                if self.cleaned_data['discount_rate']:
                    month_discount = month_amount * self.cleaned_data['discount_rate']
                elif available_discount and available_amount < month_amount:
                    if available_discount >= (month_amount - available_amount):
                        month_discount = month_amount - available_amount
                    else:
                        month_discount = available_discount
                    available_discount -= month_discount
                month_amount -= month_discount
                payment = available_amount if available_amount < month_amount else month_amount

                available_amount -= payment
                calculated_amount += payment

                if payment == month_amount:
                    self.fees_to_delete.append(fee)
                    self.fee_lines.append(FeeLine(lot=self.lot, date=fee.date, amount=payment))
                elif not payment.is_zero():
                    if not month_discount.is_zero():
                        # this error string appears also on create_receipt.html
                        raise ValidationError({'amount': _("Fees can't be paid partially when using a discount amount or rate.")})
                    else:
                        fee.amount = month_amount - payment
                        self.fees_to_update.append(fee)
                        self.fee_lines.append(FeeLine(lot=self.lot, date=fee.date, amount=payment))

    def save(self, commit=True):
        pass
