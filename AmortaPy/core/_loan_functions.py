from __future__ import annotations

def calculate_total_period_payment(loan_amount:int|float, nominal_period_interest_rate:float, number_of_periods:int|float) -> float:
    """Calculate the total payment per peirod given the Loan Amount, nominal interest rate and number of peirod payments

    Args:
        loan_amount (int | float): \n\t\tTotal Loan Amount EG `525000.00` | `525000` 
        nominal_period_interest_rate (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`
        number_of_periods (int | float): \n\t\tNumber of period payments in the Loan: Eg if 30 years paid monthly: `30*12 = 360`

    Returns:
        float: Total Payment Per Peirod (Principal + Interest)
    """
    return loan_amount * (
        (nominal_period_interest_rate * (1+nominal_period_interest_rate)**number_of_periods) 
         / 
        ((1+nominal_period_interest_rate)**number_of_periods - 1)
    )

def calculate_interst_payment(outstanding_loan_amount:int|float, nominal_period_interest_rate:float) -> float:
    """Calculate the interest payment for a period given the current outstanding loan amount and the nominal period interest rate.

    Args:
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_period_interest_rate (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: interst payment fo the period
    """
    return (outstanding_loan_amount * nominal_period_interest_rate)

def calculate_principal_payment(total_period_payment:int|float, outstanding_loan_amount:int|float, nominal_period_interest_rate:float) -> float:
    """Calculate the principal payment for the given peirod based on the total period payment for the current outstaing loan balance 
    and the applicable nominal interest rate 

    Args:
        total_period_payment (int | float): \n\t\tAmount paid per period EG: `2200` per month.
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_period_interest_rate (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        float: principal payment for the period
    """
    return total_period_payment - calculate_interst_payment(outstanding_loan_amount, nominal_period_interest_rate)

def calculate_principal_and_interest_payment(total_period_payment:int|float, outstanding_loan_amount:int|float, nominal_period_interest_rate:float) -> tuple[float, float]:
    """Calculate the principal and interest portions of a period payment given the total period payment for the current outstaing loan balance 
    and the applicable nominal interest rate  

    Args:
        total_period_payment (int | float): \n\t\tAmount paid per period EG: `2200` per month.
        outstanding_loan_amount (int | float):  \n\t\tOustanding Loan Amount EG `515000.00` | `515000` 
        nominal_period_interest_rate (float): \n\t\tThe interest rate per peirod. EG if `4% Annual`, and payments monthly: `0.04/12 = 0.003333`

    Returns:
        tuple[float, float]: (`principal_payment`, `interest_payment`)
    """
    return (
        calculate_principal_payment(total_period_payment, outstanding_loan_amount, nominal_period_interest_rate), 
        calculate_interst_payment(outstanding_loan_amount, nominal_period_interest_rate)
    )
