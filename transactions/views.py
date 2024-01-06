
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from . forms import TransactionForm,DepositForm,WithdrawForm,LoanRequestForm
from django.views.generic import CreateView,ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .constants import DEPOSIT,WITHDRAW,LOAN,LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
# Create your views here.

# ai akta view diye Diposit,WIthdraw,loan er kaj korbo
class TransactionCreateMixin(LoginRequiredMixin,CreateView):
    model=Transaction
    template_name='transactions/transaction_form.html'
    title=''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs=super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title
        })
        return context
    

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


class TransactionReportView(LoginRequiredMixin,ListView):
    template_name=''
    model=Transaction
    balance=0

    def get_queryset(self):
        # user kono filter na korle sob data dekhabe
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str=self.request.GET.get('start_date')
        end_date_str=self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date=datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date=datetime.strptime(end_date_str, '%Y-%m-%d').date()
            queryset = queryset.filter(timestamp_date_gte=start_date, timestamp_date_lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp_date_gte=start_date, timestamp_date_lte=end_date).aggregate(Sum('amount'))['amount__sum']
            
        else:
            self.balance=self.request.user.account.balance
        
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account
        })
        return context

class PayLoanView(LoginRequiredMixin,View):
    def get(self,request,loan_id):
        loan=get_object_or_404(Transaction,id=loan_id)

        if loan.loan_approve:
            user_account =loan.account
            if loan.amount < user_account.balance:
                user_account -= loan.amount
                loan.balance_after_transaction=user_account.balance
                user_account.save()
                loan.transaction_type=LOAN_PAID
                loan.save()
                return redirect()
            else:
                messages.error(self.request,f'Loan amount ia greater than available balance')
                return redirect()
            
class LoanListView(LoginRequiredMixin,ListView):
    model=Transaction
    template_name=''
    context_object_name='loans'

    def get_queryset(self):
        user_account=self.request.user.account
        queryset=Transaction.objects.filter(account=user_account,transaction_type=3)
        return queryset