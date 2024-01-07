from django.db import models
from accounts.models import UserBankAccount
from . constants import TRANSACTION_TYPE
# Create your models here.

class Transaction(models.Model):
    account=models.ForeignKey(UserBankAccount,on_delete=models.CASCADE,
        related_name='transactions') #multiple transactions hote pare
    receiver_account = models.ForeignKey(UserBankAccount,on_delete=models.CASCADE,
        related_name='received_transactions',
        blank=True,
        null=True
    )
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(
        decimal_places=2,max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    loan_approve=models.BooleanField(default=False)
    is_bankrupt=models.BooleanField(default=False)
    def __str__(self):
        return str(self.account.account_no)
    

    class Meta:
        ordering= ['timestamp']


