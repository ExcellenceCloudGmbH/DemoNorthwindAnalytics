"""Seed the data the dashboards read.

    lex seed_northwind

Idempotent — `get_or_create` throughout, so running it twice changes nothing.
Every page of `_streamlit_structure.py` needs rows to show; the Calculations
page in particular needs a `FundValuation` to point at.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

CURRENCIES = [("EUR", "Euro"), ("USD", "US Dollar"), ("GBP", "Pound Sterling")]

FUNDS = [
    ("Alpha Growth Fund",  "USD", "1500000.00", "equity",       True),
    ("Beta Income Fund",   "EUR", "3200000.50", "fixed_income", True),
    ("Gamma Multi Fund",   "GBP",  "800000.00", "multi_asset",  True),
    ("Delta Equity Fund",  "USD", "5000000.00", "equity",       False),
    ("Epsilon Bond Fund",  "EUR", "2100000.75", "fixed_income", True),
]

POSITIONS = [
    ("Alpha Growth Fund", "AAPL",  "1000", "150000.00", "technology"),
    ("Alpha Growth Fund", "MSFT",   "800", "240000.00", "technology"),
    ("Alpha Growth Fund", "JNJ",    "500",  "80000.00", "healthcare"),
    ("Beta Income Fund",  "US10Y", "2000", "210000.00", "financials"),
    ("Beta Income Fund",  "SHEL",   "900", "185000.00", "energy"),
    ("Gamma Multi Fund",  "TSLA",   "300",  "75000.00", "technology"),
    ("Gamma Multi Fund",  "PFE",    "700",  "42000.00", "healthcare"),
    ("Delta Equity Fund", "AMZN",   "400", "160000.00", "consumer"),
    ("Delta Equity Fund", "GOOGL",  "250", "130000.00", "technology"),
    ("Epsilon Bond Fund", "UK10Y", "1500", "165000.00", "financials"),
]


class Command(BaseCommand):
    help = "Seed Northwind's currencies, funds, positions and one valuation."

    def handle(self, *args, **options):
        from Input.Currency import Currency
        from Input.Fund import Fund
        from Input.Position import Position
        from Reports.FundValuation import FundValuation

        currencies = {}
        for code, name in CURRENCIES:
            currencies[code], _ = Currency.objects.get_or_create(
                code=code, defaults={"name": name})

        funds = {}
        for name, code, nav, strategy, active in FUNDS:
            funds[name], _ = Fund.objects.get_or_create(
                name=name,
                defaults={
                    "currency": currencies[code],
                    "nav": Decimal(nav),
                    "strategy": strategy,
                    "is_active": active,
                },
            )

        for fund_name, instrument, qty, value, sector in POSITIONS:
            Position.objects.get_or_create(
                fund=funds[fund_name],
                instrument=instrument,
                defaults={
                    "quantity": Decimal(qty),
                    "market_value": Decimal(value),
                    "sector": sector,
                },
            )

        # The Calculations page needs one to point at. Left uncalculated on
        # purpose: pressing the control is the thing that page demonstrates.
        FundValuation.objects.get_or_create(fund=funds["Alpha Growth Fund"])

        self.stdout.write(self.style.SUCCESS(
            f"Northwind seeded: {Currency.objects.count()} currencies, "
            f"{Fund.objects.count()} funds, {Position.objects.count()} positions, "
            f"{FundValuation.objects.count()} valuation."
        ))
