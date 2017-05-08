from django.contrib import admin
from .models import Lot, Contact


class ContactInline(admin.TabularInline):
    model = Contact
    fields = ['name', 'phone_number', 'is_owner']
    extra = 2


class ContactAdmin(admin.ModelAdmin):
    fields = ['name', 'phone_number', 'is_owner']
    list_display = ('name', 'phone_number', 'is_owner')
    list_filter = ['is_owner']
    search_fields = ['name']


class LotAdmin(admin.ModelAdmin):
    inlines = [ContactInline]
    list_display = ('code', 'address')
    search_fields = ['code', 'address']


admin.site.register(Lot, LotAdmin)
admin.site.register(Contact, ContactAdmin)
