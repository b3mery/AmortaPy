from __future__ import annotations

import pandas as pd
import numpy as np
import numpy_financial as npf

from ._constants import Constants as const

def repayment_frequency_name(repayment_frequency:int|float) -> str:
    """Return the repayment frequency name that corresponds to the number of periods.

    Args:
        repayment_frequency (int | float): Repayment frequency periods as int or float
  
    Raises:
        ValueError: If repayment frequency is not valid

    Returns:
        str: Repaymet Frequency Name in lower case
    """
    if int(repayment_frequency) == const.WEEKLY_PERIODS: 
        return const.WEEKLY_NAME.lower()
    if int(repayment_frequency) == const.FORTNIGHTLY_PERIODS: 
        return const.FORTNIGHTLY_NAME.lower()
    if int(repayment_frequency) == const.MONTHLY_PERIODS: 
        return const.MONTHLY_NAME.lower()
    if int(repayment_frequency) not in const.VALID_REPAYMENT_PERIODS:
         raise ValueError(f'Repayment Frequency must be one of `{const.VALID_REPAYMENT_PERIODS}`')       

def repayment_frequency_periods(repayment_frequency:str) -> int: 
    """Get the number of peirods for the given str repayment_frequency type.

    Args:
        repayment_frequency (str): a repayment frequency name

    Raises:
        ValueError: If repayment frequency is not valid

    Returns:
        int: Repayment period values
    """
    if repayment_frequency.lower() == const.WEEKLY_NAME.lower(): 
        return const.WEEKLY_PERIODS
    if repayment_frequency.lower() == const.FORTNIGHTLY_NAME.lower(): 
        return const.FORTNIGHTLY_PERIODS
    if repayment_frequency.lower() == const.MONTHLY_NAME.lower(): 
        return const.MONTHLY_PERIODS
    if repayment_frequency.lower() not in const.VALID_REPAYMENT_NAMES:
        raise ValueError(f'Repayment Frequency must be one of `{const.VALID_REPAYMENT_NAMES}`')


class LoanAmortization:
    """Loan Amortization Schedule Calculator
    """
    _repayment_frequency_periods:int = const.MONTHLY_PERIODS
    _nominal_annual_interest_rate: float
    _loan_amount: int|float
    _years:int|float
    _n_peirods: int|float
    _interest_compound_frequency:int|float = const.DAILY
    _effective_annual_interest_rate: float
    _df: pd.DataFrame

    def __init__(self,nominal_annual_interest_rate:float, loan_amount:int|float, years:int|float, repayment_frequency:str|int|float|None = None, interest_compound_frequency:int|float|None = None) -> None:
        self._nominal_annual_interest_rate = nominal_annual_interest_rate
        self._years = years
        self._loan_amount = loan_amount
        if repayment_frequency is not None:
            self.update_repayment_frequency_periods(repayment_frequency)
        if interest_compound_frequency is not None:
            self._interest_compound_frequency = interest_compound_frequency
        self._generate_amortization_schedule()
        self.calculate_effective_annual_interest_rate()

    def update_repayment_frequency_periods(self, repayment_frequency:str|int|float):
        self._repayment_frequency_periods = self._get_repayment_frequency_periods(repayment_frequency)
        self._generate_amortization_schedule()
        return self

    def calculate_effective_annual_interest_rate(self):
        """            
        Effective Annual Interest Rate (EAR) Formula: `(1 + i/n)^n -1`.
        Where: 
                `i` is the Nominal Annual Interest Rate, and
                `n` is the number of compounded periods. 
        For Example:
        * Interest compounded monthly `n=12`
        * Interest compounded daily `n=365`
        """
        self._effective_annual_interest_rate = ((1 + (self._nominal_annual_interest_rate/self._interest_compound_frequency))**self._interest_compound_frequency) - 1
        return self

    def _get_repayment_frequency_periods(self, repayment_frequency:str|int|float|None) ->int:
        if repayment_frequency is None:
            return self._repayment_frequency_periods
        if isinstance(repayment_frequency, str):
            return repayment_frequency_periods(repayment_frequency)
        if repayment_frequency_name(repayment_frequency):
            return int(repayment_frequency)

    def _nominal_interest_rate_per_period(self, nominal_annual_interest_rate:float, repayment_frequency:int|str|None = None) -> float:
        """The Nominal Annual Interest Rate divided by the number of peirods in the repayment frequency

        Args:
            nominal_annual_interest_rate (float): Nominal Annual Interest Rate expressed a `decimal` not as a `percent`. eg. `4.00%` = `0.04` and `4.65%` = `0.0465`.
            repayment_frequency (int | str | None, optional): [`monthly` | `12`, `fortnightly` | `26`, or `weekly` | `52` ]. Defaults to None. If None will use default `cls.repayment_frequency`

        Returns:
            float: The Nominal Annual Interest Rate divided by the number of peirods in the repayment frequency
            Example: `0.0394 / 12` -> `0.003283333333333333`
        """
        return nominal_annual_interest_rate / self._get_repayment_frequency_periods(repayment_frequency)

    def calculate_number_of_periods(self, years:int,  repayment_frequency:str|int|float|None = None) -> int:
        """_summary_

        Args:
            years (int): _description_
            repayment_frequency (int | None, optional): _description_. Defaults to None.

        Returns:
            int: _description_
        """
        return years * self._get_repayment_frequency_periods(repayment_frequency)

    def _generate_amortization_schedule(self):
        """Generate an Amortization Loan Repayment Schedule

        Args:
            nominal_annual_interest_rate (float): Nominal Annual Interest Rate expressed a `decimal` not as a `percent`. eg. `4.00%` = `0.04` and `4.65%` = `0.0465`.
            loan_amount (int | float): The amount being loaned expressed as a `int` or `float` eg: `$500,000` = `5e5` or `500000` or `500000.00`.
            years (int): number of years the loan is for. EG `30` years.
            repayment_frequency (int | str | None, optional): The repayment frequency of the loan, expressed as int or str:
            [( `12` or  `Monthly`) or (`26` or `Fortnightly`) (`52` or `Weekly`)].
            \t*Defaults to `None`. If `None`, by default will use `Loan.repayment_frequency`

        Returns:
            pd.DataFrame: The Loan Amortization Schedule of repayments in order of repayment
        """

        mortgage_amount = -(self._loan_amount) 
        nominal_interest_rate_per_period = self._nominal_interest_rate_per_period(self.nominal_annual_interest_rate, self.repayment_frequency_periods)
        periods = self.calculate_number_of_periods(self.years, self.repayment_frequency_periods)
        # Create Number of Periods Array
        n_periods = np.arange(self.years * self.repayment_frequency_periods) + 1

        interest_monthly = npf.ipmt(nominal_interest_rate_per_period, n_periods, periods, mortgage_amount)
        principal_monthly = npf.ppmt(nominal_interest_rate_per_period, n_periods, periods, mortgage_amount)

        df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
        df = pd.DataFrame(df_initialize, columns=['period','interest','principal'])

        df['period_payment'] = df['interest'] + df['principal']

        df['outstanding_interest']  = df['interest'].cumsum()
        df['outstanding_principal']  = df['principal'].cumsum()

        df.outstanding_interest = df.outstanding_interest.values[::-1]
        df.outstanding_principal = df.outstanding_principal.values[::-1]

        df['outstanding_balance'] = df.period_payment.cumsum()
        df.outstanding_balance = df.outstanding_balance.values[::-1]

        self._df = df
        return self

    @property
    def repayment_frequency_name(self):
        return repayment_frequency_name(self._repayment_frequency_periods)
    
    @property
    def repayment_frequency_periods(self):
        return self._repayment_frequency_periods

    @property
    def nominal_annual_interest_rate(self):
        return self._nominal_annual_interest_rate

    @property
    def loan_amount(self):
        return self._loan_amount

    @property
    def years(self):
        return self._years
    
    @property
    def amortization_schedule(self) -> pd.DataFrame:
        return self._df
    
    @property
    def interest_compound_frequency(self):
        return self._interest_compound_frequency

    @property
    def effective_annual_interest_rate(self):
        return self._effective_annual_interest_rate

    @property
    def total_interest(self) ->float:
        return self.amortization_schedule[:1].outstanding_interest[0]

    # def __repr__(self) -> str:
    #     return str(self._df)