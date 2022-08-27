from __future__ import annotations
from argparse import ArgumentError

import pandas as pd

def calculate_total_period_payment(loan_amount:int|float,
                                   nominal_interest_rate_per_period:float,
                                   number_of_periods:int|float) -> float:
    """Calculate the `PMT` - payment per peirod given the Loan Amount, nominal interest rate and number of peirod payments

    Args:
        loan_amount (int | float): \n\t\tTotal Loan Amount EG `525000.00` | `525000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`
        number_of_periods (int | float): \n\t\tNumber of period payments in the Loan: Eg if 30 years paid monthly: `30*12 = 360`

    Returns:
        float: Total Payment Per Peirod (Principal + Interest) `PMT`
    """
    return loan_amount * (
        (nominal_interest_rate_per_period * (1+nominal_interest_rate_per_period)**number_of_periods)   / 
        ((1+nominal_interest_rate_per_period)**number_of_periods - 1)     )

def calculate_interest_payment(outstanding_loan_amount:int|float,
                              nominal_interest_rate_per_period:float) -> float:
    """Calculate the `IPMT` - interest payment for a period given the current outstanding loan amount and the nominal period interest rate.

    Args:
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: interst payment fo the period `IPMT`
    """
    return (outstanding_loan_amount * nominal_interest_rate_per_period)

def calculate_principal_payment(total_period_payment:int|float,
                                outstanding_loan_amount:int|float,
                                nominal_interest_rate_per_period:float) -> float:
    """Calculate the `PPMT` - principal payment for the given peirod based on the total period payment for the current outstaing loan balance 
    and the applicable nominal interest rate 

    Args:
        total_period_payment (int | float): \n\t\tAmount paid per period EG: `2200` per month.
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: principal payment for the period - `PPMT`
    """
    return total_period_payment - calculate_interest_payment(outstanding_loan_amount, nominal_interest_rate_per_period)

def calculate_principal_and_interest_payment(total_period_payment:int|float,
                                             outstanding_loan_amount:int|float,
                                             nominal_interest_rate_per_period:float) -> tuple[float, float]:
    """Calculate the principal (`PPMT`) and interest (`IPMT`) portions of a period payment given the total period payment for the current outstaing loan balance 
    and the applicable nominal interest rate  

    Args:
        total_period_payment (int | float): \n\t\tAmount paid per period EG: `2200` per month.
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        tuple[float, float]: (`principal_payment`, `interest_payment`)
    """
    return (
        calculate_principal_payment(total_period_payment, outstanding_loan_amount, nominal_interest_rate_per_period), 
        calculate_interest_payment(outstanding_loan_amount, nominal_interest_rate_per_period)
    )

def generate_amortization_table(nominal_interest_rate_per_period:float,
                                principal_amount:int|float,
                                number_of_periods:int|float,
                                total_payment_per_period: int|float|None=None,
                                additional_payment_per_period: int|float|None=None,
                                interest_only_rate_per_period:float=0.00,
                                number_of_interest_only_periods:int|float=0 ) -> pd.DataFrame:
    """Generate a Amortization Repaymet table as a `pandas.DataFrame`

    Args:
        nominal_interest_rate_per_period (float): The quote annual interest rate `3.85%` divided by the repayment frequency. Monthly would be passed as `0.0385/12`
        principal_amount (int | float): The principal amount borrowed `545000.00`
        number_of_periods (int | float): Number of periods over the life of the loan. EG: `30 years` paid `monthly` = `30*12` 
        total_payment_per_period (int | float | None, optional): Optional total payment per period `PMT` you intend to make. Defaults to None. Func will calculate the payment by default.
         If `total_payment_per_period` is passed it will need to be >= the expected minium `PMT`, if it is not, the calculated minium PMT will be used. 
        additional_payment_per_period (int | float | None, optional): Optional additional payment per period you intend to make, will be added to `total_payment_per_period`. Defaults to None.
        interest_only_rate_per_period (int | float, optional): The quote annual interest rate for the intertest periods, `4.14%` divided by the repayment frequency. Monthly would be passed as `0.0414/12`
        number_of_interest_only_periods (int | float, optional): The interest only periods of the loan. EG: `1 year` paid `monthly` = `1*12` 

    Returns:
         pd.DataFrame: Amortization Repayment Schedule Table
    """
    # Evaluate the Params
    if (interest_only_rate_per_period > 0.00 and number_of_interest_only_periods <= 0) or (interest_only_rate_per_period <= 0.00 and number_of_interest_only_periods > 0): 
        raise ArgumentError(None, "To calculate interest only, you need to pass valid args to `interest_only_rate_per_period` and `number_of_interest_only_periods`")
    
    n_principal_payment_periods = number_of_periods - number_of_interest_only_periods
    expected_total_period_payment = calculate_total_period_payment(principal_amount, nominal_interest_rate_per_period, n_principal_payment_periods)

    if total_payment_per_period is None or total_payment_per_period < expected_total_period_payment:
        total_payment_per_period = expected_total_period_payment

    if additional_payment_per_period is not None:
        total_payment_per_period = total_payment_per_period + additional_payment_per_period
    
    # Init data dict
    data = {
        'period': [],
        'opening_balance' : [],
        'interest': [],
        'principal': [], 
        'period_payment': [],
        'closing_balance': []
    }

    # Iterate through periods until the peirods are complete or the loan is $0.00
    opening_loan_balance = principal_amount
    for period in range(1, number_of_periods+1):
        
        if (interest_only_rate_per_period > 0.00 and number_of_interest_only_periods > 0) and period <= number_of_interest_only_periods:
            interest = opening_loan_balance * interest_only_rate_per_period
            principal = 0 
            period_payment = interest

        else:
            principal, interest = calculate_principal_and_interest_payment(total_payment_per_period, opening_loan_balance, nominal_interest_rate_per_period)
            period_payment = total_payment_per_period

        closing_loan_balance = opening_loan_balance - principal
        if closing_loan_balance < 0:
            principal += closing_loan_balance
            closing_loan_balance = 0
            period_payment = principal + interest

        data['period'].append(period)
        data['opening_balance'].append(opening_loan_balance)
        data['interest'].append(interest)
        data['principal'].append(principal)
        data['period_payment'].append(period_payment)
        data['closing_balance'].append(round(closing_loan_balance, 6))

        opening_loan_balance = closing_loan_balance
        if opening_loan_balance <= 0: 
            break 
    df = pd.DataFrame(data=data)
    # Sum interest from bottom up then reverse and add as column 
    df['cumulative_interest']  = df['interest'][::-1].cumsum()[::-1]
    return df
