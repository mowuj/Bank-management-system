from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):

    class Meta:
        model=Transaction
        fields=['amount','transaction_type']

    def __init__(self,*args,**kwargs):
        self.account=kwargs.pop('account')
        super.__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # field ti disable thakbe
        self.fields['transaction_type'].widget= forms.HiddenInput() # user er kase hide thakbe
    
    def save(self,commit=True):
        self.instance.account=self.account
        self.instance.balance_after_transaction=self.account.balance
        return super().save()
    
class DepositForm(TransactionForm):
    def clean_amount(self): # amount field k filter korbo
        min_deposit_amount = 500
        amount = self.cleaned_data.get('amount') # user er fill up kora field theka value ta nichi
        if amount < min_deposit_amount: 
            raise forms.ValidationError(
                f'You Have to Deposit at least {min_deposit_amount} $'
            )
        return amount
    
class WithdrawForm(Transaction):
    def clean_amount(self):
        account=self.account
        min_withdraw_amount = 500 
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.clean_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You have to withdraw more than {min_withdraw_amount}'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
            f'You can withdraw less than {max_withdraw_amount}'
            )
        
        if amount > balance:
            raise forms.ValidationError(
            f'You have {balance} $ in your account.
            You can not withdraw more than your balance'
            )
        return amount
    
class LoanRequestForm(Transaction):
    def clean_amount(self):
        amount=self.cleaned_data.get('amount')

        return amount