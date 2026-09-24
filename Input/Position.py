from django.db import models

from lex.core.models.LexModel import LexModel

from Input.Fund import Fund


class Position(LexModel):
    """One holding inside a fund.

    `related_name="positions"` is what lets `Fund.streamlit_main` and
    `FundValuation.calculate` reach these without a query of their own.
    """

    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name="positions")
    instrument = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    market_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sector = models.CharField(
        max_length=50,
        choices=[
            ("technology", "Technology"),
            ("healthcare", "Healthcare"),
            ("financials", "Financials"),
            ("energy", "Energy"),
            ("consumer", "Consumer"),
        ],
        default="technology",
    )

    def __str__(self):
        return f"{self.fund.name} — {self.instrument}"
