from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Lot, Contact


class LotResource(resources.ModelResource):
    class Meta:
        model = Lot


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact


class ContactInline(admin.TabularInline):
    model = Contact
    fields = ['name', 'phone_number', 'is_owner']
    extra = 2


class ContactAdmin(ImportExportModelAdmin):
    fields = ['name', 'phone_number', 'is_owner']
    list_display = ('name', 'phone_number', 'is_owner')
    list_filter = ['is_owner']
    search_fields = ['name']
    resource_class = ContactResource


class LotAdmin(ImportExportModelAdmin):
    inlines = [ContactInline]
    list_display = ('code', 'address')
    search_fields = ['code', 'address']
    resource_class = LotResource


admin.site.register(Lot, LotAdmin)
admin.site.register(Contact, ContactAdmin)
