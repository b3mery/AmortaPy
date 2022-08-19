"""API Functions
"""
from __future__ import annotations
from .core._loan_amortization import LoanAmortization


def generate_loan_amortization_schedule(nominal_annual_interest_rate:float,
                                        loan_amount:int|float,
                                        years:int|float,
                                        repayment_frequency:str|int|float|None = None) -> LoanAmortization:
    return LoanAmortization(nominal_annual_interest_rate, loan_amount, years, repayment_frequency)