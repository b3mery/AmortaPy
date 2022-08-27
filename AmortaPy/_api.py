"""API Functions
"""
from __future__ import annotations
from .core._amortization import Amortization


def generate_amortization_schedule(nominal_annual_interest_rate:float,
                                   principal_amount:int|float,
                                   years:int|float,
                                   repayment_frequency:str|int|float|None = None,
                                   interest_only_nominal_annual_interest_rate:float|None=None,
                                   interest_only_years:int|float|None=None
                                   ) -> Amortization:
    """Configure Amortization Schedule 

    Args:
        nominal_annual_interest_rate (float): nominal annual interest rate EG: `3.94%` = `0.0394`
        principal_amount (int | float): The principal amount `515000` or `515000.00`
        years (int | float): The amortization years eg `30` or `30.0`
        repayment_frequency (str | int | float | None, optional): repayment frequency, `monthly`|`12`, or `fortnightly`|`26`, or `weekly`|`52`.
         Defaults to None. If None configured default will be used.
        interest_only_nominal_annual_interest_rate (float | None, optional): The quoted annual interest only interest rate eg `4.14` = `0.0414`. Defaults to None.
        interest_only_years (int | float | None, optional): The years at interest only. EG `1` or `1.0`. Defaults to None.

    Returns:
        Amortization: Instantiated Amortization instance
    """                                
    return Amortization(nominal_annual_interest_rate, principal_amount, years, repayment_frequency, interest_only_nominal_annual_interest_rate, interest_only_years)