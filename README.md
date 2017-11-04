CondoREST is a django application to keep track of income and expenses for a small condo or group of houses.
It has the following modules:

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
