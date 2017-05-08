from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Lot(models.Model):
    code = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.code


class Contact(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    phone_number = PhoneNumberField()

    def __str__(self):
        return self.name
