# CondoREST

CondoREST is a django application to keep track of income and expenses for a small condo or group of houses.
It has the following modules:

## Getting Started

### Prerequisites

This project uses Python 3 and Postgres 9+ with tablefunc EXTENSION installed.

To install Python 3:

    sudo apt-get install python3 // in ubuntu
    brew install python3 // in macos

To install PostgreSQL in Mac you can use [PostgresAPP](https://postgresapp.com/). In ubuntu:

    sudo apt-get install postgresql

It is recommendable to install using a virtual environment. If you enjoy using fish shell you can use
[virtual fish](http://virtualfish.readthedocs.io/en/latest/). BUT, since we're using python3 these instructions won't work.

Install virtualfish by running:

    pip3 install virtualfish

Add the following to your `~/.config/fish/config.fish`:

    eval (python3 -m virtualfish compat_aliases auto_activation)

After closing and opening your console you will need to switch to fish shell, most likely you would be using regular bash by default.

Change to fish by running:

    fish

Then you should be able to do:

    vf new condorest

This will install a virtual environment with several different Python packages that will be used on this specific project, independent of others virtual environments that may be used in other projects. Since the virtual environments are stored on a hidden folder inside your home folder, it doesn't matter where you run this specific command.

Go to your project folder, if not currently on it:

    cd condorest-django

Then continue with the following commands:

    vf activate condorest
    vf connect # to use the auto-activation plugin
    # http://virtualfish.readthedocs.io/en/latest/plugins.html#auto-activation
    python --version # this should give you python 3
    cd ..
    vf deactivate
    python --version # this should give you python 2
    cd condorest-django # condorest env is now auto activated ;-)
    python --version # this should give you python 3 because of the autoactivation

vf connect use the auto-activation plugin, this means that the next time you get to your project folder the version of python initially configured (in this case python3) will be used everytime from now on.

We keep track of requirements using requirements.txt file, you can install them using `pip install -r requirements.txt`.

We use also a non pip installable extension called django-monthfield. To install, make sure you are using
the condorest virtualenv before running this commands:

    git clone https://github.com/clearspark/django-monthfield.git
    cd django-monthfield
    python setup.py install
    cd ..
    rm -rf django-monthfield

### Installing

Create your local `.env` file based on the template file `local.env`.

Create a database and user on your postgres server. For example running this commands (if using ubuntu append `sudo -u postgres` to both commands):

    createuser -Psd condorest
    createdb -O condorest condorest

You need to create a database for the project and make sure your credentials are correct on the file `.env`.
After that just run `python manage.py migrate`.

To install the `tablefunc` postgres extension run this on your postgres database:

    CREATE EXTENSION tablefunc;

### Importing data

There is an example script that imports data from google spreadsheets using this sheets as a model:

- [Contacts](https://docs.google.com/spreadsheets/d/1E1_ycmwKa420c04p9YeN-1W6dnJY8PcLwYs-NNSwO6k/edit?usp=sharing)
- [Cash account](https://docs.google.com/spreadsheets/d/1yVpoOauNMssMKDWu-RB9HH9l_YOC9tBxhPXYWi_70Ls/edit#gid=1312790969)
- [Fees](https://docs.google.com/spreadsheets/d/1lv2OYSm96-MZvUhL_nI63FjIzSch2K30MlUnYE9fv8s/edit#gid=833310425)

To set up access to this spreadsheets from python you can follow
[this tutorial](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html).

To import them you use the commands (in this order):

    python manage.py google_import contacts
    python manage.py google_import cash_account
    python manage.py google_import fees
    
**Warning**. This commands delete previously entered entries, receipts, expense notes, fees and even contacts.
    
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

