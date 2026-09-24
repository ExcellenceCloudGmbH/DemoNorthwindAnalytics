from django.db import models

from lex.core.models.LexModel import LexModel


class Currency(LexModel):
    """The currency a fund reports in.

    A small reference table, and the target of `Fund.currency`. Hovering a
    fund's currency chip in the grid previews this record, so the fields here
    are the ones that make sense out of context.
    """

    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.code
