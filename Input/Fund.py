from django.db import models
from rest_framework import serializers

from lex.core.models.LexModel import LexModel

from Input.Currency import Currency


class Fund(LexModel):
    """A fund: what it is worth, what it invests in, and in which currency."""

    name = models.CharField(max_length=200)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    inception_date = models.DateField(null=True, blank=True)
    nav = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    strategy = models.CharField(
        max_length=50,
        choices=[
            ("equity", "Equity"),
            ("fixed_income", "Fixed Income"),
            ("multi_asset", "Multi Asset"),
        ],
        default="equity",
    )
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name

    def streamlit_main(self, user=None):
        """The record-level dashboard, shown by this record's Analytics tab.

        `streamlit_main` runs with `self` bound to one record, so everything
        here is about this fund. The Calculate control at the bottom is the
        same one the record page uses -- the calculation runs and reports back
        without leaving the dashboard.
        """
        import pandas as pd
        import streamlit as st

        from lex.lex_app.streamlit import lex_calculation

        st.subheader(self.name)

        positions = list(self.positions.values("instrument", "market_value"))
        left, right = st.columns(2)
        left.metric("NAV", f"{self.nav:,.2f}")
        right.metric("Positions", len(positions))

        if positions:
            frame = pd.DataFrame(positions).set_index("instrument")
            st.bar_chart(frame["market_value"])
        else:
            st.info("No positions yet.")

        valuation = self.valuations.first()
        if valuation is not None:
            st.caption("Recalculate this fund's valuation without leaving the dashboard:")
            lex_calculation("fundvaluation", pk=valuation.pk)


class FundSummarySerializer(serializers.ModelSerializer):
    """A deliberately narrow view of a fund.

    Registered as ``summary`` so a dashboard can ask for it by name:
    ``lex_view("fund", serializer="summary")``. The point of a second
    serializer is that the embedded table shows the columns this audience
    needs and not the ones it does not -- the framework's own columns
    (created/edited by and when) are absent here.
    """

    currency = serializers.CharField(source="currency.code", read_only=True)

    class Meta:
        model = Fund
        fields = ["id", "name", "currency", "nav", "strategy", "is_active"]


Fund.api_serializers = {"summary": FundSummarySerializer}
