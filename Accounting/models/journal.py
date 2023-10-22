from django.db import models, transaction

from Accounting.models.accounts import Account


class JournalEntry(models.Model):
    class Statuses(models.TextChoices):
        INITIATED = 'INITIATED', 'Initiated'
        COMMITTED = 'COMMITTED', 'Committed'
        FAILED = 'FAILED', 'Failed'

    description = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Statuses.choices, default=Statuses.INITIATED)

    @transaction.atomic
    def commit(self):
        if self.status != self.Statuses.INITIATED:
            raise ValueError("Cannot commit a journal entry not in initiated state.")

        # Locking related stuff
        journal_entry = JournalEntry.objects.select_for_update().get(pk=self.pk)
        journal_lines = JournalLine.objects.select_for_update().filter(journal_entry=journal_entry)
        accounts_to_update = Account.objects.select_for_update().filter(journal_lines__in=journal_lines)
        bank_transaction = BankTransaction.objects.select_for_update().filter(journal_entry=journal_entry).first()

        if bank_transaction and bank_transaction.status != BankTransaction.Statuses.SUCCESSFUL:
            raise ValueError("Cannot commit a journal entry without a confirmed bank transaction.")

        for journal_line in journal_lines:
            if journal_line.debit:
                journal_line.account.balance += journal_line.debit
            else:
                journal_line.account.balance -= journal_line.credit
            journal_line.account.save()

        journal_entry.status = self.Statuses.COMMITTED
        journal_entry.save()


class JournalLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='journal_lines')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='journal_lines')
    debit = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    credit = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)

    def __str__(self):
        if self.debit:
            return f"+{self.debit} to {self.account} - {self.journal_entry}"
        return f"-{self.credit} from {self.account} - {self.journal_entry}"


class BankTransaction(models.Model):
    class Statuses(models.TextChoices):
        INITIATED = 'INITIATED', 'Initiated'  # created
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'  # has token
        SUCCESSFUL = 'SUCCESSFUL', 'Successful'
        FAILED = 'FAILED', 'Failed'

    token = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    journal_entry = models.OneToOneField(JournalEntry, on_delete=models.CASCADE, related_name='bank_transaction')
    status = models.CharField(
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.INITIATED
    )
