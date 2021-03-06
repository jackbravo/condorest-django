# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 03:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('type', models.CharField(choices=[('asset', 'Asset'), ('expense', 'Expense'), ('liability', 'Liability'), ('equity', 'Equity'), ('revenue', 'Revenue')], db_index=True, max_length=20)),
                ('contra', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('details', models.CharField(max_length=254, blank=True, null=True)),
                ('date', models.DateField(db_index=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=13)),
                ('debit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ledger.Account', related_name='debit_entries')),
                ('credit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ledger.Account', related_name='credit_entries')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['date', 'id'],
            },
        ),
    ]
