from __future__ import annotations

import pandas as pd

def calculate_total_period_payment(loan_amount:int|float,
                                   nominal_interest_rate_per_period:float,
                                   number_of_periods:int|float) -> float:
    """Calculate the total payment per peirod given the Loan Amount, nominal interest rate and number of peirod payments

    Args:
        loan_amount (int | float): \n\t\tTotal Loan Amount EG `525000.00` | `525000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`
        number_of_periods (int | float): \n\t\tNumber of period payments in the Loan: Eg if 30 years paid monthly: `30*12 = 360`

    Returns:
        float: Total Payment Per Peirod (Principal + Interest)
    """
    return loan_amount * (
        (nominal_interest_rate_per_period * (1+nominal_interest_rate_per_period)**number_of_periods)   / 
        ((1+nominal_interest_rate_per_period)**number_of_periods - 1)     )

def calculate_interest_payment(outstanding_loan_amount:int|float,
                              nominal_interest_rate_per_period:float) -> float:
    """Calculate the interest payment for a period given the current outstanding loan amount and the nominal period interest rate.

    Args:
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: interst payment fo the period
    """
    return (outstanding_loan_amount * nominal_interest_rate_per_period)

def calculate_principal_payment(total_period_payment:int|float,
                                outstanding_loan_amount:int|float,
                                nominal_interest_rate_per_period:float) -> float:
    """Calculate the principal payment for the given peirod based on the total period payment for the current outstaing loan balance 
    and the applicable nominal interest rate 

    Args:
        total_period_payment (int | float): \n\t\tAmount paid per period EG: `2200` per month.
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_interest_rate_per_period (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: principal payment for the period
    """
    return total_period_payment - calculate_interest_payment(outstanding_loan_amount, nominal_interest_rate_per_period)

def calculate_principal_and_interest_payment(total_period_payment:int|float,
                                             outstanding_loan_amount:int|float,
                                             nominal_interest_rate_per_period:float) -> tuple[float, float]:
    """Calculate the principal and interest portions of a period payment given the total period payment for the current outstaing loan balance 
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

def generate_amortization_table(loan_amount:int|float,
                                   nominal_interest_rate_per_period:float,
                                   number_of_periods:int|float,
                                   total_payment_per_period: int|float|None=None,
                                   additional_payment_per_period: int|float|None=None ) -> pd.DataFrame:
    """_summary_

    Args:
        loan_amount (int | float): _description_
        nominal_interest_rate_per_period (float): _description_
        number_of_periods (int | float): _description_
        total_payment_per_period (int | float | None, optional): _description_. Defaults to None.
        additional_payment_per_period (int | float | None, optional): _description_. Defaults to None.
    """
    # Evaluate the Params
    expected_total_period_payment = calculate_total_period_payment(loan_amount, nominal_interest_rate_per_period, number_of_periods)

    if total_payment_per_period is None or total_payment_per_period < expected_total_period_payment:
        total_payment_per_period = expected_total_period_payment

    if additional_payment_per_period is not None:
        print('add')
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
    opening_loan_balance = loan_amount
    for period in range(1, number_of_periods+1):
        principal, interest = calculate_principal_and_interest_payment(total_payment_per_period, opening_loan_balance, nominal_interest_rate_per_period)
        closing_loan_balance = opening_loan_balance - principal
        if closing_loan_balance < 0:
            principal += closing_loan_balance
            closing_loan_balance = 0
            total_payment_per_period = principal + interest

        data['period'].append(period)
        data['opening_balance'].append(opening_loan_balance)
        data['interest'].append(interest)
        data['principal'].append(principal)
        data['period_payment'].append(total_payment_per_period)
        data['closing_balance'].append(round(closing_loan_balance, 6))

        opening_loan_balance = closing_loan_balance
        if opening_loan_balance <= 0: 
            break 
    
    return pd.DataFrame(data=data)
