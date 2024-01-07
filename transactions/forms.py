from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type'
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')  # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        # ei field disable thakbe
        self.fields['transaction_type'].disabled = True
        # user er theke hide kora thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):  # amount field ke filter korbo
        min_deposit_amount = 100
        # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance  # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance:  # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount


class TransferForm(TransactionForm):
    receiver_account = forms.ModelChoiceField(
        queryset=UserBankAccount.objects.all(), label='Receiver Account'
    )

    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type',
            'receiver_account'
        ]

    def clean_amount(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        receiver_account = cleaned_data.get('receiver_account')
        sender_account = self.account


        if receiver_account == sender_account:
            raise forms.ValidationError("Cannot transfer to your own account.")

        if receiver_account and amount:
            if amount > sender_account.balance:
                raise forms.ValidationError(
                    f'You have {sender_account.balance} $ in your account. '
                    'You cannot transfer more than your account balance.'
                )

            receiver_account_exists = UserBankAccount.objects.filter(
                id=receiver_account.id).exists()
            if not receiver_account_exists:
                raise forms.ValidationError("Receiver account does not exist.")

        return amount

    def save(self, commit=True):
        print("Inside save method of TransferForm")
        sender_account = self.account
        receiver_account = self.cleaned_data.get('receiver_account')
        amount = self.cleaned_data.get('amount')

        return super().save(commit)


