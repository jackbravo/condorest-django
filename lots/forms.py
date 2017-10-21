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
