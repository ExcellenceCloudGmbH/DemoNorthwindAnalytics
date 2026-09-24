from decimal import Decimal

from django.db import models

from lex.core.models.CalculationModel import CalculationModel

from Input.Fund import Fund


class FundValuation(CalculationModel):
    """Sums a fund's positions into `total_market_value`.

    A `CalculationModel` contributes the `is_calculated` status field and the
    state machine behind it. Override `calculate()` and mutate `self` -- do not
    call `self.save()`; the framework persists the result and moves the status
    to SUCCESS, or to ERROR with the traceback in
    `calculation_error_message`.
    """

    fund = models.ForeignKey(
        Fund, on_delete=models.CASCADE, related_name="valuations", null=True
    )
    total_market_value = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )
    #: The framework writes the traceback here on failure if the field exists.
    calculation_error_message = models.TextField(blank=True, default="")

    def __str__(self):
        fund_name = self.fund.name if self.fund_id else "(no fund)"
        return f"Valuation — {fund_name}"

    def calculate(self):
        """Sum the fund's positions. The log is half of what this produces.

        The `Calculations` page of the dashboard shows the live log, the
        execution tree and the consolidated log side by side. A calculation
        that writes nothing leaves those three widgets correct and empty,
        which documents the plumbing rather than the feature -- so this one
        logs a heading, a table and a summary line as it goes.
        """
        from lex.audit_logging.handlers.LexLogger import LexLogger

        if self.fund_id is None:
            LexLogger().add_text("No fund attached; nothing to value.").log()
            self.total_market_value = Decimal("0.00")
            return

        LexLogger().add_heading(f"Valuing {self.fund.name}", level=2).log()

        positions = list(self.fund.positions.all())
        total = Decimal("0.00")
        rows = []
        for position in positions:
            value = position.market_value or Decimal("0.00")
            total += value
            rows.append([position.instrument, f"{value:,.2f}"])

        if rows:
            LexLogger().add_table(headers=["Instrument", "Market value"], rows=rows).log()
        else:
            LexLogger().add_text("No positions on this fund.").log()

        LexLogger().add_text(
            f"{len(positions)} position(s) summed to {total:,.2f}."
        ).log()

        self.total_market_value = total
