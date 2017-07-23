from django.contrib import admin
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
    search_fields = ['name']
    resource_class = ContactResource


class LotAdmin(ImportExportModelAdmin):
    list_display = ('name', 'address')
    search_fields = ['name', 'address']
    resource_class = LotResource


admin.site.register(LotType)
admin.site.register(Lot, LotAdmin)
admin.site.register(Contact, ContactAdmin)
