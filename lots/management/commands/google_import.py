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
from revenue.models import Receipt, Fee, FeeLine


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
            'fees': self.import_fees,
        }

        for type in options['type']:
            types.get(type, self.error_handler)(client)

    def error_handler(self, client):
        raise CommandError('Your import option does not exist')

    def import_fees(self, client):
        Fee.objects.all().delete()
        FeeLine.objects.all().delete()
        Receipt.objects.filter(details__contains='Import').delete()

        file = client.open("R/ LOTES 2016.xlsx")
        for year in range(2009, 2018):
            sheet = file.worksheet(str(year))
            records = sheet.get_all_values()
            #handle = open(str(year) + '.v2.json')
            #records = json.load(handle)
            #handle.close()
            self._import_fees_records(year, records)

        self.fill_empty_receipt_amounts()

        print("Finished importing fees")

    def fill_empty_receipt_amounts(self):
        from django.db import connection
        with connection.cursor() as cursor:
            sql = '''UPDATE revenue_receipt r
              SET amount = COALESCE((SELECT SUM(amount) FROM revenue_feeline f WHERE receipt_id = r.id), 0.00)
              WHERE r.amount = 0.00
            '''
            cursor.execute(sql)

    def _import_fees_records(self, year, records):
        months = 12 if year != 2009 else 7
        first_receipt_cell = 6 if year != 2009 else 16
        start_date = datetime(year=year, month=13-months, day=1)
        min_receipt_number = '1351'
        cash = Account.objects.get(name='Cash')
        for row in records[3:]:
            if not row[4]:
                break
            lot = Lot.objects.get(name='M' + row[4] + '-L' + row[5])
            lot.default_fee = self.parse_decimal(row[34]) / months
            lot.save()

            if not lot.default_fee:
                continue

            fee_list = []
            feeline_list = []
            receipt_numbers = []
            has_amount_without_receipt = False
            receipts_below_min = {}
            year_receipt = None
            # an enumeration with month number as key and receipt_cell number as value
            my_enum = enumerate(range(first_receipt_cell, first_receipt_cell + (months*2), 2), start=start_date.month)
            for month, receipt_cell in my_enum:
                amount_cell = receipt_cell+1
                date = datetime(year=year, month=month, day=1)
                amount = self.parse_decimal(row[amount_cell])
                if not amount:
                    fee_list.append(Fee(lot=lot, date=date, amount=lot.default_fee))
                else:
                    feeline_list.append(FeeLine(lot=lot, date=date, amount=amount))
                    if row[receipt_cell] != '':
                        feeline_list[-1].receipt_number = row[receipt_cell] # placeholder
                        if int(row[receipt_cell]) < int(min_receipt_number) and row[receipt_cell] not in receipts_below_min:
                            receipt = Receipt(contact=lot.owner, date=date, save_in_ledger=False, amount=Decimal('0.00'),
                                                   number=row[receipt_cell], debit_account=cash, details='Import')
                            receipt.save()
                            receipts_below_min[receipt.number] = receipt.id
                        else:
                            receipt_numbers.append(row[receipt_cell])
                    else:
                        has_amount_without_receipt = True

            if fee_list:
                Fee.objects.bulk_create(fee_list)

            if has_amount_without_receipt:
                year_receipt = Receipt(contact=lot.owner, date=start_date, save_in_ledger=False, amount=Decimal('0.00'),
                                       details='Import: Pago de cuota sin recibo', debit_account=cash)
                year_receipt.save()

            ids_dict = dict(list(Receipt.objects.filter(number__in=receipt_numbers).values_list('number', 'id')))
            ids_dict.update(receipts_below_min)
            for feeline in feeline_list:
                if hasattr(feeline, 'receipt_number'): feeline.receipt_id = ids_dict[feeline.receipt_number]
                else: feeline.receipt_id = year_receipt.id
            FeeLine.objects.bulk_create(feeline_list)

        print("Finished importing fees for year", year)

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

        file = client.open("R/ I-E MANTENIMIENTO.xlsx")
        for sheet_name in sheets:
            sheet = file.worksheet(sheet_name)
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
