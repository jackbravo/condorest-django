from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from lots.forms import CreateFeesForm, UpdateFeeForm
from revenue.models import Fee
from .models import Lot, Contact, LotType


class LotResource(resources.ModelResource):
    class Meta:
        model = Lot


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact


class ContactAdmin(ImportExportModelAdmin):
    list_display = ['name', 'phone_number']
    search_fields = ['name']
    resource_class = ContactResource


class LotAdmin(ImportExportModelAdmin):
    list_display = ['name', 'address', 'owner', 'default_fee', 'lot_type']
    list_filter = ['lot_type']
    list_select_related = ['owner', 'lot_type']
    search_fields = ['name', 'address', 'owner__name']
    resource_class = LotResource

    actions = ['create_fees', 'update_fee']

    def create_fees(self, request, queryset):
        if 'update' in request.POST:
            form = CreateFeesForm(request.POST)

            if form.is_valid():
                ids = tuple(queryset.values_list('id', flat=True))
                count = Fee.create_fees(ids, form.cleaned_data['start_date'], form.cleaned_data['end_date'])
                self.message_user(
                    request,
                    "Created {} fees".format(count)
                )
                return HttpResponseRedirect(request.get_full_path())

        else:
            form = CreateFeesForm(initial={
                '_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                'select_across': request.POST['select_across']
            })

        return render(request, 'admin/lots_create_fees.html', context={
            'form': form,
            'lots': queryset,
        })

    def update_fee(self, request, queryset):
        if 'update' in request.POST:
            form = UpdateFeeForm(request.POST)

            if form.is_valid():
                count = form.update_fee(queryset)
                self.message_user(
                    request,
                    "Changed default fee on {} lots".format(count)
                )
                return HttpResponseRedirect(request.get_full_path())

        else:
            form = UpdateFeeForm(initial={
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
