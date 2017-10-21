# Requirements:
# - pip install gspread oauth2client
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from expense.models import ExpenseNote
from ledger.models import Account, Entry
from lots.models import Lot, LotType, Contact
from revenue.models import Receipt, Fee


class Command(BaseCommand):
    help = 'Import lots from '

    def add_arguments(self, parser):
        parser.add_argument('type', nargs='+', type=str)

    def handle(self, *args, **options):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        types = {
            'cash_account': self.import_cash_account,
            'contacts': self.import_contacts,
        }

        for type in options['type']:
            types.get(type, self.error_handler)(client)

    def error_handler(self, client):
        raise CommandError('Your import option does not exist')

    def import_cash_account(self, client):
        Entry.objects.all().delete()
        Receipt.objects.all().delete()
        ExpenseNote.objects.all().delete()

        sheets = ('may-16', 'jun-16', 'jul-16', 'ago-16', 'sep-16', 'oct-16', 'nov-16', 'dic-16', 'ene-17', 'feb-17', 'Mar-17', 'Abr-17', 'May-17', 'Jun-17', 'Jul-17', 'Ago-17', 'Sep-17', 'Oct-17')

        Entry(details='Saldo inicial',
              amount=Decimal('5110.62'),
              debit_account=Account.objects.get(name='Cash'),
              credit_account=Account.objects.get(name='Balance'),
              date='2016-05-01').save()

        for sheet_name in sheets:
            sheet = client.open("R/ I-E MANTENIMIENTO.xlsx").worksheet(sheet_name)
            records = sheet.get_all_records(head=5)
            self._import_cash_account_records(records)
            print('Finished:', sheet_name)

        print("Finished importing cash_account")

    def _import_cash_account_records(self, records):
        administrative = Account.objects.get(name='Administrative')
        cash = Account.objects.get(name='Cash')
        bank = Account.objects.get(name='Bank')

        income = Decimal('0.00')
        expense = Decimal('0.00')
        current_date = datetime.now()
        for row in records:
            try:
                current_date = datetime.strptime(row['Fecha'], '%d-%m-%y') if row['Fecha'] != '' else current_date
            except ValueError:
                print('Error while parsing date with row', row)
            owner = Contact.objects.filter(owns_lots__name=row['Clave']).first() if row['Clave'] != '' else None
            if row['Ingreso'] != '' and row['Egreso'] != '':
                ingreso = self.parse_decimal(row['Ingreso'])
                egreso = self.parse_decimal(row['Egreso'])
                if ingreso == income and egreso == expense:
                    break
            if row['Ingreso'] != '':
                amount = self.parse_decimal(row['Ingreso'])
                if row['Folio']:
                    item, created = Receipt.objects.get_or_create(
                        number=row['Folio'],
                        defaults={
                            'number': row['Folio'],
                            'amount': amount,
                            'date': current_date,
                            'debit_account': cash,
                            'contact': owner,
                            'details': '''Lote: %(Clave)s, Cuotas: %(Cuotas)s
                            Nombre: %(Nombre)s''' % row,
                        }
                    )
                    if not created:
                        print('Error with old receipt', row)
                        raise Exception('Warning, should not be an old receipt ' + row['Folio'])
                else:
                    item = Receipt(
                        amount=amount,
                        date=current_date,
                        debit_account=cash,
                        contact=owner,
                        details='''Lote: %(Clave)s, Cuotas: %(Cuotas)s
                        Nombre: %(Nombre)s''' % row,
                    )
                    item.save()
                income += amount
            elif row['Egreso'] != '':
                amount = self.parse_decimal(row['Egreso'])
                item = ExpenseNote(
                    number=row['Folio'],
                    amount=amount,
                    credit_account=cash,
                    debit_account=administrative,
                    date=current_date,
                    details=row['Concepto'],
                )
                item.save()
                expense += amount
            elif row['Banco'] != '' and row['Folio'] != '':
                amount = self.parse_decimal(row['Banco'])
                item, created = Receipt.objects.get_or_create(
                    number=row['Folio'],
                    defaults={
                        'number': row['Folio'],
                        'amount': amount,
                        'date': current_date,
                        'debit_account': bank,
                        'contact': owner,
                        'details': '''Lote: %(Clave)s, Cuotas: %(Cuotas)s
                            Nombre: %(Nombre)s''' % row,
                    }
                )
                if not created:
                    print('Error with old receipt', row)
                    raise Exception('Warning, should not be an old receipt ' + row['Folio'])

    def import_contacts(self, client):
        Contact.objects.all().delete()
        Lot.objects.all().delete()

        sheet = client.open("Vecinos y sugerencias").worksheet("DATOS DE RESIDENTES")

        # Extract and print all of the values
        records = sheet.get_all_records()

        casa = LotType.objects.get(name='Casa')
        lote = LotType.objects.get(name='Lote')

        for row in records:
            if row['M'] in ['', 'M', '0']:
                continue

            lot = Lot(name='M' + str(row['M']).zfill(2) + '-L' + str(row['L']).zfill(2), address=row['Dirección'])
            if row['Tipo'] == 'Casa':
                lot.lot_type = casa
            else:
                lot.lot_type = lote

            if row['MASCOTAS'] != '':
                lot.details = 'Mascotas: ' + row['MASCOTAS']

            if row['PROPIETARIOS'].strip() != '':
                contact, created = Contact.objects.get_or_create(
                    name__exact=row['PROPIETARIOS'],
                    defaults={'name': row['PROPIETARIOS']}
                )
                if row['CELULAR'] != '':
                    contact.phone_number = row['CELULAR']
                if row['PROFESION EL'] != '':
                    contact.details = 'Porfesión: ' + row['PROFESION EL']
                contact.save()
                lot.owner = contact

            # we need to save lots so we can save many-to-many associations
            lot.save()

            if row['ARRENDATARIOS'].strip() != '':
                values = row['ARRENDATARIOS'].split(' - ')
                contact, created = Contact.objects.get_or_create(
                    name__exact=values[0],
                    defaults={'name': values[0], 'details': 'Arrendatario'}
                )
                if len(values) > 1:
                    contact.phone_number = values[1]
                contact.save()
                lot.contacts.add(contact)

            if row['ESPOSA (O)'].strip() != '':
                contact, created = Contact.objects.get_or_create(
                    name__exact=row['ESPOSA (O)'],
                    defaults={'name': row['ESPOSA (O)']}
                )
                if row['PROFESION ELLA'] != '':
                    contact.details = 'Porfesión: ' + row['PROFESION ELLA']
                contact.save()
                lot.contacts.add(contact)

        print("Finished importing contacts")

    def parse_decimal(self, str):
        if str: return Decimal(str.strip('$').replace(',', ''))
        else: return Decimal('0.00')
