from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from month.forms import MonthField


class UpdateFeeForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    select_across = forms.BooleanField(required=False, widget=forms.HiddenInput())
    fee = forms.DecimalField()

    def update_fee(self, queryset):
        fee = self.cleaned_data['fee']
        queryset.update(default_fee=fee)
        return queryset.count()


class CreateFeesForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    select_across = forms.BooleanField(required=False, widget=forms.HiddenInput())
    start_date = MonthField(initial=timezone.now)
    end_date = MonthField(initial=timezone.now)

    def clean(self):
        if self.cleaned_data['start_date'] > self.cleaned_data['end_date']:
            raise ValidationError(_("Start date must be before the end date"))

    def create_fees(self, queryset = None):
        ids = tuple(queryset.values_list('id', flat=True))
        from django.db import connection
        with connection.cursor() as cursor:
            sql = '''INSERT INTO revenue_fee ("date", amount, lot_id)
              SELECT t::date, default_fee, id
              FROM lots_lot
              CROSS JOIN generate_series(timestamp %s, timestamp %s, '1 month') t
              WHERE id IN %s
            '''

            cursor.execute(sql, [self.cleaned_data['start_date'], self.cleaned_data['end_date'], ids])
            return cursor.rowcount
