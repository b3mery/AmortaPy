"""Constant variable module used through package.
"""
import os, pathlib
class Constants:
    """Constant Variables to be used through package.
    """
    __slots__ = ()
    WEEKLY_PERIODS = 52 
    WEEKLY_NAME = 'weekly'
    FORTNIGHTLY_PERIODS = WEEKLY_PERIODS / 2
    FORTNIGHTLY_NAME = 'fortnightly'
    MONTHLY_PERIODS = 12
    MONTHLY_NAME = 'monthly'
    DAILY = 365
    # DAILY_NAME = 'daily'
    VALID_REPAYMENT_PERIODS = [WEEKLY_PERIODS, FORTNIGHTLY_PERIODS, MONTHLY_PERIODS]
    VALID_REPAYMENT_NAMES = [WEEKLY_NAME.lower(),FORTNIGHTLY_NAME.lower(), MONTHLY_NAME.lower()]
    YEARS = 30

    # Loan Amort Inplace
    INPLACE = True

    # Default Export Path
    EXCEL_EXPORT_PATH = './Amortization_Table.xlsx'

    TEMPLATES_FOLDER = os.path.join(pathlib.Path(__file__).parent.parent, 'templates')