from django.contrib.auth.models import User
from django.db import models, transaction


class Moneypool(models.Model):
    name = models.CharField(max_length=40)
    members = models.ManyToManyField(User, related_name='moneypools')

    def __str__(self):
        return f"{self.name} moneypool"


class Cashbox(models.Model):
    name = models.CharField(max_length=40)
    members = models.ManyToManyField(User, related_name='cashboxes')

    def __str__(self):
        return f"{self.name} cashbox"


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    iban = models.CharField(max_length=26)


class PaymentGateway(models.Model):
    name = models.CharField(max_length=20)


class Account(models.Model):
    """
    Main model used for Accounting purposes. Every "thing" that we can pay to, or get paid from, is an Account.
    """

    class Types(models.TextChoices):
        WALLET = 'WALLET', 'User Wallet'
        MONEYPOOL = 'MONEYPOOL', 'Moneypool Account'
        CASHBOX = 'CASHBOX', 'Cashbox Account'
        BANK_ACCOUNT = 'BANK_ACCOUNT', 'Bank Account'
        PAYMENT_GATEWAY = 'PAYMENT_GATEWAY', 'Payment Gateway'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moneypool = models.ForeignKey(Moneypool, on_delete=models.CASCADE)
    cashbox = models.ForeignKey(Cashbox, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE)

    type = models.CharField(max_length=20, choices=Types.choices)
    balance = models.DecimalField(max_digits=15, decimal_places=0)

    def __str__(self):
        if self.type == self.Types.WALLET:
            return f"{self.user}'s Wallet"
        if self.type == self.Types.MONEYPOOL:
            return f"{self.moneypool} Moneypool Account"
        if self.type == self.Types.CASHBOX:
            return f"{self.cashbox} Cashbox Account"
        if self.type == self.Types.BANK_ACCOUNT:
            return f"{self.bank_account} Bank Account"
        if self.type == self.Types.PAYMENT_GATEWAY:
            return f"{self.payment_gateway} Payment Gateway Account"
