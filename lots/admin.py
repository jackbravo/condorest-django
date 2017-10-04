from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Lot, Contact, LotType


class LotResource(resources.ModelResource):
    class Meta:
        model = Lot


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact


class ContactAdmin(ImportExportModelAdmin):
    list_display = ['name', 'phone_number']
    ordering = ['name']
    search_fields = ['name']
    resource_class = ContactResource


class LotAdmin(ImportExportModelAdmin):
    list_display = ['name', 'address', 'owner', 'default_fee', 'lot_type']
    list_filter = ['lot_type']
    list_select_related = ['owner', 'lot_type']
    ordering = ['name']
    search_fields = ['name', 'address']
    resource_class = LotResource

    actions = ['update_fee']

    class UpdateFeeForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        select_across = forms.BooleanField(required=False, widget=forms.HiddenInput())
        fee = forms.DecimalField()

    def update_fee(self, request, queryset):
        if 'update' in request.POST:
            form = self.UpdateFeeForm(request.POST)

            if form.is_valid():
                fee = form.cleaned_data['fee']
                queryset.update(default_fee=fee)

                self.message_user(
                    request,
                    "Changed default fee on {} lots".format(queryset.count())
                )
                return HttpResponseRedirect(request.get_full_path())

        else:
            form = self.UpdateFeeForm(initial={
                '_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                'select_across': request.POST['select_across']
            })

        return render(request, 'admin/lots_update_fee.html', context={
            'form': form,
            'lots': queryset,
        })


admin.site.register(LotType)
admin.site.register(Lot, LotAdmin)
admin.site.register(Contact, ContactAdmin)
