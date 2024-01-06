from django.shortcuts import render
from . forms import TransactionForm,DepositForm,WithdrawForm,LoanRequestForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .constants import DEPOSIT,WITHDRAW,LOAN,LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
# Create your views here.

# ai akta view diye Diposit,WIthdraw,loan er kaj korbo
class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    model=Transaction
    template_name=''
    title=''
    success_url=''

    def get_form_kwargs(self):
        kwargs=super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
    

class DepositMoneyView(TransactionCreateMixin):
    form_class=DepositForm
    title = 'Deposit Money'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self,form):
        amount=form.cleaned_data.get('amount')
        account=self.request.user.account
        account.balance += amount
        account.save(
            update_fields=['balance']
        )
        messages.success(self.request,f"{amount}$ was deposited to your account successfully")
        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAW}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance -= amount
        account.save(
            update_fields=['balance']
        )
        messages.success(
            self.request, f"{amount}$ was withdraw from your account successfully")
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        current_loan_count=Transaction.objects.filter(account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse('You have crossed yot limits')
        messages.success(
            self.request, f"Loan request for amount {amount}$ has been successfully sent to admin.Wait for approval")
        return super().form_valid(form)
