"""API Functions
"""
from __future__ import annotations
from .core._amortization import Amortization


def generate_amortization_schedule(nominal_annual_interest_rate:float,
                                   principal_amount:int|float,
                                   years:int|float,
                                   repayment_frequency:str|int|float|None = None) -> Amortization:
    """Configure Amortization Schedule 

    Args:
        nominal_annual_interest_rate (float): nominal annual interest rate EG: `3.94%` = `0.0394`
        principal_amount (int | float): The principal amount `515000` or `515000.00`
        years (int | float): The amortization years eg `30` or `30.0`
        repayment_frequency (str | int | float | None, optional): repayment frequency, `monthly`|`12`, or `fortnightly`|`26`, or `weekly`|`52`. Defaults to None.
        If None configured default will be used.
    Returns:
        Amortization: Instantiated Amortization instance
    """                                
    return Amortization(nominal_annual_interest_rate, principal_amount, years, repayment_frequency)