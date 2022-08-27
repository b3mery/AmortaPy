"""Loan Amortization Module
Contains:
    * Class Helper Functions
    * Class `LoanAmortization`

"""
from __future__ import annotations
from typing_extensions import Self

import pandas as pd

from ._constants import Constants as const
from ._amortization_functions import generate_amortization_table, calculate_total_period_payment
from .._utils import build_inline_css_style_sheet
from ._plots import plot_stacked_bar_chart

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

class Amortization:
    """Amortization Schedule Calculator
    """
    _repayment_frequency_periods:int = const.MONTHLY_PERIODS
    _nominal_annual_interest_rate: float
    _principal_amount: int|float
    _years:int|float
    _interest_only_nominal_annual_interest_rate:float = 0.00
    _interest_only_years:int|float = 0.00
    _df: pd.DataFrame

    def __init__(self,
                 nominal_annual_interest_rate:float,
                 principal_amount:int|float, years:int|float,
                 repayment_frequency:str|int|float|None = None,
                 interest_only_nominal_annual_interest_rate:float|None=None,
                 interest_only_years:int|float|None=None ) -> None:
        """Configure Amortization Schedule 

        Args:
            nominal_annual_interest_rate (float): nominal annual interest rate EG: `3.94%` = `0.0394`
            principal_amount (int | float): The principal amount `515000` or `515000.00`
            years (int | float): The amortization years eg `30` or `30.0`
            repayment_frequency (str | int | float | None, optional): repayment frequency, `monthly`|`12`, or `fortnightly`|`26`, or `weekly`|`52`.
             Defaults to None. If None configured default will be used.
            interest_only_nominal_annual_interest_rate (float | None, optional): The quoted annual interest only interest rate eg `4.14` = `0.0414`.
             Defaults to None.
            interest_only_years (int | float | None, optional): The years at interest only. EG `1` or `1.0`. Defaults to None.
        """
        self._nominal_annual_interest_rate = nominal_annual_interest_rate
        self._years = years
        self._principal_amount = principal_amount
        self._interest_only_nominal_annual_interest_rate = interest_only_nominal_annual_interest_rate or 0.0
        self._interest_only_years = interest_only_years or 0.0
        if repayment_frequency is not None:
            self.set_repayment_frequency_periods(repayment_frequency)
        else:
            self._generate_amortization_schedule()

    # Getters
    @property
    def n_periods(self) -> int:
        """Number of payment periods in Loan

        Returns:
            Int: Total Peirods
        """
        return self.calculate_total_number_of_periods(self.years, self.repayment_frequency_periods)

    @property
    def repayment_frequency_name(self) -> str:
        """The repayment frequency name.
        eg: `weekly`, `fortnightly`, or `monthly`
        """
        return repayment_frequency_name(self._repayment_frequency_periods)
    
    @property
    def repayment_frequency_periods(self) -> int:
        """The Periods in the current Repayment Frequency
        """
        return self._repayment_frequency_periods

    @property
    def nominal_annual_interest_rate(self) -> float:
        """The current Nominal annual interest rate
        """
        return self._nominal_annual_interest_rate

    @property
    def principal_amount(self) -> int | float:
        """The initial Principal Amount
        """
        return self._principal_amount

    @property
    def years(self) -> int | float:
        """Current Loan Term Years
        """
        return self._years
    
    @property
    def amortization_schedule(self) -> pd.DataFrame:
        """Amortization Repayment Schedule as `Pandas.DataFrame`
        """
        return self._df

    @property
    def effective_annual_interest_rate(self) -> float:
        """Effective Annual Interest Rate (EAR) Formula: `(1 + i/n)^n -1`.

        Where: 
            * `i` is the Nominal Annual Interest Rate, and
            * `n` is the number of compounded periods. \n
        For Example:
        * Interest compounded monthly `n=12`
        * Interest compounded daily `n=365`

        Returns:
            float: `EAR`
        """
        return ((1 + (self._nominal_annual_interest_rate/self._repayment_frequency_periods))**self._repayment_frequency_periods) - 1

    @property
    def total_interest(self) ->float:
        """Calculated total interest payable under the current amortization scheduled.
        """
        return self._df['interest'].sum()

    @property
    def total_outstanding_balance(self) -> float:
        """Calculated total outstanding balance (principal + interest) under the current amortization scheduled.
        """
        return self.principal_amount + self.total_interest

    @property
    def total_interest_over_principal_per_cent(self) -> float:
        """Total Interest Payable over Total Principal - Under the current amortization schedule
        """
        return self.total_interest/self.principal_amount
    
    @property
    def total_payment_per_period(self) -> float:
        """`PMT` - Total Loan Payment Per Period  - Under the current amortization schedule

        Returns:
            float: Total Payment Per Peirod `PMT` (Principal + Interest)
        """
        return calculate_total_period_payment(
            self.principal_amount,
            self.nominal_annual_interest_rate/self.repayment_frequency_periods,
            self.n_periods - self.n_interest_only_periods
        )
    
    @property
    def period_balances_chart(self):
        """Plot Amortization Peirod Balances Principal and Interest in a Stacked Bar Chart.
        """
        df  = self.amortization_schedule.rename(
            columns={'opening_balance' : 'Outstanding Principal ($)', 'cumulative_interest' : 'Cumulative Interest Paybale ($)', 'period': 'Period'}, 
            inplace=False
        )

        chart_layout = {
            'title': 'Amortization Period Balances Over Time (n)',
            'xaxis_title':'n - Number of Repayment Periods',
            'yaxis_title':'Peirod Payments ($)',
            'legend_title':'Legend'
        }
        return plot_stacked_bar_chart(df, 'Period', [ 'Outstanding Principal ($)', 'Cumulative Interest Paybale ($)'], chart_layout)

    @property
    def period_repayments_chart(self):
        """Plot Amortization Repayments Principal and Interest in a Stacked Bar Chart 
        """
        df  = self.amortization_schedule.rename(
            columns={'principal':'Principal Payment ($)', 'interest':'Interest Payment ($)', 'period': 'Period'}, 
            inplace=False
        )
        chart_layout = {
            'title': 'Amortization Period Repayments Over Time (n)',
            'xaxis_title':'n - Number of Repayment Periods',
            'yaxis_title':'Peirod Payments ($)',
            'legend_title':'Legend'
        }
        return plot_stacked_bar_chart(df, 'Period', ['Principal Payment ($)', 'Interest Payment ($)'], chart_layout)

    @property
    def has_interest_only(self) -> bool:
        """Is proportion of the amortization schedule interest only.
        """
        if self._interest_only_nominal_annual_interest_rate > 0.0 and self._interest_only_years > 0:
            return True
        return False
    
    @property
    def interest_only_years(self) -> int|float:
        """Number of years at interest only"""
        return self._interest_only_years

    @property
    def interest_only_nominal_annual_interest_rate(self)->float:
        """The interest only nominal annual interest rate"""
        return self._interest_only_nominal_annual_interest_rate

    @property
    def n_interest_only_periods(self) -> int:
        """Number of interest only periods in the amortization schedule"""
        return self.calculate_total_number_of_periods(self.interest_only_years, self.repayment_frequency_periods)

    @property
    def interest_only_payment_per_period(self) -> float:
        """Interest only payment per period"""
        if not self.has_interest_only:
            return 0.00
        return self.principal_amount * self.interest_only_nominal_annual_interest_rate / self.repayment_frequency_periods

    @property 
    def total_interest_only_payments(self) -> float:
        """Total Interest payable over the interest only periods"""
        return self.interest_only_payment_per_period * self.repayment_frequency_periods * self.interest_only_years
    
    # Setters
    def set_repayment_frequency_periods(self, repayment_frequency:str|int|float, inplace:bool = const.INPLACE) -> Amortization | Self:
        """Set/Update/Change the current repayment frequency peirods.

        Args:
            repayment_frequency (str | int | float): Valid repayment frequency
            inplace (bool, optional): Wether to update the instance or return new instance. Defaults to True, Updates Instance.

        Returns:
            LoanAmortization | Self
        """
        if inplace:
            self._repayment_frequency_periods = self._get_repayment_frequency_periods(repayment_frequency)
            return self._generate_amortization_schedule()
        return self.copy().set_repayment_frequency_periods(repayment_frequency, inplace=True)
        
    def set_years(self, years:int|float, inplace:bool = const.INPLACE) -> Amortization | Self:
        """Update the loan years

        Args:
            years (int | float): Loan Repayment Years
            inplace (bool, optional): Wether to update the instance or return new instance. Defaults to True, Updates Instance.

        Returns:
            LoanAmortization | Self
        """
        if inplace:
            self._years = years
            return self._generate_amortization_schedule()
        return self.copy().set_years(years, inplace=True)

    def set_nominal_annual_interest_rate(self, nominal_annual_interest_rate:float, inplace:bool = const.INPLACE) -> Amortization | Self:
        """Update the Nominal Annual Interest Rate and recalculate loan

        Args:
            nominal_annual_interest_rate (float): The nominal annual interest rate as a float `3.94%` = `0.0394`
            inplace (bool, optional): Wether to update the instance or return new instance. Defaults to True, Updates Instance.

        Returns:
            LoanAmortization | Self 
        """
        if inplace:
            self._nominal_annual_interest_rate = nominal_annual_interest_rate
            return self._generate_amortization_schedule()
        return self.copy().set_nominal_annual_interest_rate(nominal_annual_interest_rate, True)

    def set_interest_only(self, interest_only_nominal_annual_interest_rate:float, interest_only_years:int|float, inplace:bool = const.INPLACE) -> Amortization | Self:
        """Update the interest only portions of the amortization schedule.

        Args:
            interest_only_nominal_annual_interest_rate (float): Nominal annual interest rate for interest only
            interest_only_years (int | float): Loan Repayment Years
            inplace (bool, optional): Wether to update the instance or return new instance. Defaults to True, Updates Instance.

        Returns:
            LoanAmortization | Self
        """
        if inplace:
            self._interest_only_nominal_annual_interest_rate = interest_only_nominal_annual_interest_rate
            self._interest_only_years = interest_only_years
            return self._generate_amortization_schedule()
        return self.copy().set_interest_only(interest_only_nominal_annual_interest_rate,interest_only_years, inplace=True)

    # Private Methods
    def _get_repayment_frequency_periods(self, repayment_frequency:str|int|float|None) -> int:
        """Get and validate the repayment periods for a given frequency

        Args:
            repayment_frequency (str | int | float | None): The loan term repayment frequency. Defaults to None. 
            Will use instance repayment frequency if None

        Returns:
            int: Repayment Frequency periods 
        """
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
        df = generate_amortization_table(
            self._nominal_interest_rate_per_period(self.nominal_annual_interest_rate, self.repayment_frequency_periods),
            self.principal_amount,
            self.n_periods,
            interest_only_rate_per_period=self._nominal_interest_rate_per_period(self.interest_only_nominal_annual_interest_rate, self.repayment_frequency_periods),
            number_of_interest_only_periods=self.n_interest_only_periods
        )
        self._df = df
        return self
    
    # Public Methods
    def calculate_total_number_of_periods(self, years:int|float,  repayment_frequency:str|int|float|None = None) -> int:
        """Calculate the expected number of payment peirods given the `years` and `repayment frequency`

        Args:
            years (int|float): Loan Term Years
            repayment_frequency (int | None, optional): The loan term repayment frequency. Defaults to None.

        Returns:
            int: Expect number of payment periods
        """
        return years * self._get_repayment_frequency_periods(repayment_frequency)

    def export_amortization_schedule_to_excel(self, export_path:str|bytes = const.EXCEL_EXPORT_PATH, engine:str = 'openpyxl'):
        """Export the amortization table dataframe to excel.

        Args:
            export_path (str | bytes | None, optional): Excel file export path. Defaults to const.EXCEL_EXPORT_PATH.
            engine (str, optional): Write engine to use, `openpyxl` or `xlsxwriter`. Defaults to 'openpyxl'.
        """
        self.amortization_schedule.to_excel(export_path, index=False, engine=engine)

    def copy(self) -> Amortization:
        """Copy Object

        Returns:
            LoanAmortization: New instantiated version of object 
        """
        return Amortization(
            self.nominal_annual_interest_rate,
            self.principal_amount,
            self.years,
            self.repayment_frequency_periods,
            self.interest_only_nominal_annual_interest_rate,
            self.interest_only_years
        )
    
    def __copy__(self) -> Amortization:
        """Shallow Copy

        Returns:
            LoanAmortization: New instantiated version of object 
        """
        return self.copy()

    def __deepcopy__(self, memo=None) -> Amortization:
        """Deep Copy

        Args:
            memo: Defaults to None. Default Standard syntax, not used

        Returns:
            LoanAmortization: New instantiated version of object 
        """
        return self.copy()
    
    def _repr_interest_only(self) ->str|None:
        if not self.has_interest_only:
            return None

        report = f"""----
        Interest Only Repayments Per Peirod:    ${self.interest_only_payment_per_period :0,.2f}
        Interest Only Annual Interest Rate:     {self.interest_only_nominal_annual_interest_rate * 100 :0.2f}%   
        Forecasted Total Interest Only:         ${self.total_interest_only_payments :0,.2f}
        Total Interest Only / Total Interest:   {self.total_interest_only_payments/self.total_interest * 100 :0.2f}%
        """
        return report

    def __repr__(self) -> str:
        interest_only_repr = self._repr_interest_only()
        report = f"""
        --------------------------------------------------------------------
        Amortization Schedule
        --------------------------------------------------------------------
        Principal Borrowed:                     ${self.principal_amount :0,.2f}
        Years:                                  {self.years}
        Annual Interest Rate:                   {self.nominal_annual_interest_rate*100 :0.2f}%
        Forecasted Total Interest:              ${self.total_interest :0,.2f}
        Repayment Frequency:                    {self.repayment_frequency_name.title()} - {self.n_periods :0,.0f} Periods 
        Minimum Repayments Per Peirod:          ${self.total_payment_per_period :0,.2f}
        Effective Annual Interest Rate (EAR)    {self.effective_annual_interest_rate * 100 :0.2f}%         
        Total Interest / Total Principal:       {self.total_interest_over_principal_per_cent * 100 :0.2f}%
        {interest_only_repr if interest_only_repr else ''}
        --------------------------------------------------------------------
        """ 
        return report

    def _repr_interest_only_html(self) ->str|None:
        if not self.has_interest_only:
            return None

        report = f"""
            <tr>
                <th>Interest Repayments Per Peirod</th>
                <th>Interest Only Annual Interest Rate</th>
                <th>Forecasted Total Interest Only</th>
                <th>Total Interest Only / Total Interest</th>
            </tr>
            <tr>
                <td>${self.interest_only_payment_per_period :0,.2f}</td>
                <td>{self.interest_only_nominal_annual_interest_rate * 100 :0.2f}%</td>              
                <td>${self.total_interest_only_payments :0,.2f}</td>
                <td>{self.total_interest_only_payments/self.total_interest * 100 :0.2f}%</td>
            </tr>
        """
        return report


    def _repr_html_(self):
        style_sheet = build_inline_css_style_sheet(f"{const.TEMPLATES_FOLDER}/styles.css")
        interest_only_repr = self._repr_interest_only_html()
        report = f"""
        {style_sheet if style_sheet else ''}
        <h1>Amortization Schedule</h1>
        <table class='amort-summary'>
            <tr>
                <th>Principal Borrowed</th>
                <th>Years</th>
                <th>Annual Interest Rate</th>
                <th>Forecasted Total Interest</th>
            </tr>
            <tr>
                <td>${self.principal_amount :0,.2f}</td>
                <td>{self.years}</td>
                <td>{self.nominal_annual_interest_rate*100 :0.2f}%</td>
                <td>${self.total_interest :0,.2f}</td>
            </tr>
            <tr>
                <th>Repayment Frequency</th>
                <th>Minimum Repayments Per Peirod</th>
                <th>Effective Annual Interest Rate (EAR)</th>
                <th>Total Interest / Total Principal</th>
            </tr>
            <tr>
                <td>{self.repayment_frequency_name.title()} - {self.n_periods :0,.0f} Periods</td> 
                <td>${self.total_payment_per_period :0,.2f}</td>
                <td>{self.effective_annual_interest_rate * 100 :0.2f}%</td>              
                <td>{self.total_interest_over_principal_per_cent * 100 :0.2f}%</td>
            </tr>
            {interest_only_repr if interest_only_repr else ''}
        </table>
        """
        return report