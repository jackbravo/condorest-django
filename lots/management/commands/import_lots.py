from django.core.management.base import BaseCommand
import re
import csv

from lots.models import Lot, LotType, Contact


class Command(BaseCommand):
    help = 'Import lots from a .csv file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        with open(options['file'], newline='') as csv_file:
            reader = csv.reader(csv_file)
            casa = LotType.objects.get(name='Casa')
            lote = LotType.objects.get(name='Lote')
            for row in reader:
                if row[0] in ['', 'M', '0']:
                    continue

                lot = Lot(name='M' + row[0].zfill(2) + '-L' + row[1].zfill(2), address=row[4])
                if row[5] == 'Casa':
                    lot.lot_type = casa
                else:
                    lot.lot_type = lote

                if row[15] != '':
                    lot.details = 'Mascotas: ' + row[15]

                if row[2].strip() != '':
                    contact, created = Contact.objects.get_or_create(
                        name__exact=row[2],
                        defaults={'name': row[2]}
                    )
                    if row[6] != '':
                        contact.phone_number = row[6]
                    if row[11] != '':
                        contact.details = 'Porfesión: ' + row[11]
                    contact.save()
                    lot.owner = contact

                # we need to save lots so we can save many-to-many associations
                lot.save()

                if row[3].strip() != '':
                    values = row[2].split(' - ')
                    contact, created = Contact.objects.get_or_create(
                        name__exact=values[0],
                        defaults={'name': values[0], 'details': 'Arrendatario'}
                    )
                    if len(values) > 1:
                        contact.phone_number = values[1]
                    contact.save()
                    lot.contacts.add(contact)

                if row[8].strip() != '':
                    contact, created = Contact.objects.get_or_create(
                        name__exact=row[8],
                        defaults={'name': row[8]}
                    )
                    if row[9] != '':
                        contact.phone_number = row[9]
                    if row[12] != '':
                        contact.details = 'Porfesión: ' + row[12]
                    contact.save()
                    lot.contacts.add(contact)
