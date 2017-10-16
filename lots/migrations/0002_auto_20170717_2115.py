# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 02:15
from __future__ import unicode_literals

from django.db import models, migrations, connection

from lots.models import LotType, Lot
from revenue.models import Fee, Receipt


def load_data(apps, schema_editor):
    LotType = apps.get_model("lots", "LotType")

    LotType(name="Casa").save()
    LotType(name="Lote").save()


def remove_data(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM lots_lot_contacts')
        cursor.execute('DELETE FROM lots_contact')
        cursor.execute('DELETE FROM lots_lot')
        cursor.execute('DELETE FROM lots_lottype')


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data, remove_data)
    ]
