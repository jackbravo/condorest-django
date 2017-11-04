# CondoREST

CondoREST is a django application to keep track of income and expenses for a small condo or group of houses.
It has the following modules:

## Getting Started

### Prerequisites

This project uses Python 3 and Postgres 9+.

It is recommendable to install using a virtual environment. If you enjoy using fish shell you can use
[virtual fish](http://virtualfish.readthedocs.io/en/latest/). And then do:

    vf new condorest
    cd condorest
    vf activate condorest
    vf connect # to use the auto-activation plugin
    # http://virtualfish.readthedocs.io/en/latest/plugins.html#auto-activation
    cd ..
    cd deactivate
    cd condorest # condorest env is now auto activated ;-)

We keep track of requirements using requirements.txt file, you can install them using `pip install -r requirements.txt`.

### Installing

You need to create a database for the project and make sure your credentials are correct on `condorest/settings.py`.
After that just run `python manage.py migrate`.

### Importing data

There is an example script that imports data from google spreadsheets using this sheets as a model:

- Cash account: https://docs.google.com/spreadsheets/d/1yVpoOauNMssMKDWu-RB9HH9l_YOC9tBxhPXYWi_70Ls/edit#gid=1312790969
- Fees: https://docs.google.com/spreadsheets/d/1lv2OYSm96-MZvUhL_nI63FjIzSch2K30MlUnYE9fv8s/edit#gid=833310425

To import them you use the commands (in this order):

    python manage.py google_import cash_account
    python manage.py google_import fees
    
### Running

Done, now you can test the site using `python manage.py runserver`

## Projects

### Lots

Keeps track of the lots or houses and contacts for each.

### Ledger

Organizes income and expenses in a simple [double entry accounting system](https://en.wikipedia.org/wiki/Double-entry_bookkeeping_system).
There is an entry table to capture the flow of money between accounts. Each entry item has a debit account and a credit
account. Accounts have 2 debit types:

- Asset (eg. bank, cash)
- Expense (eg. administrative, purchases, salary)

and 3 credit types:

- Liability
- Equity (eg. balance)
- Revenue (eg. fees, deposits)

### Revenue

Revenue can be recorded using receipts. Lots have monthly fees that are owed to the condo. Receipts can have fee_lines
that indicate which month was paid. When paying fees you can have discounts.

### Expense

Expenses can be recorded using expense notes. Both receipts and expense notes inherit from a Ledger abstract model
called IncomeExpenseNote that creates an entry for each receipt or expense note if the field save_in_ledger is `True`.

