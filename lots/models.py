from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=254, blank=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LotType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Lot(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True)
    lot_type = models.ForeignKey(LotType, on_delete=models.PROTECT)
    default_fee = models.DecimalField(max_digits=13, decimal_places=2, default=100.00)
    owner = models.ForeignKey(Contact, related_name='owns_lots', blank=True, null=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    details = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
