"""Northwind Analytics — the Streamlit surface of a Lex App project.

`lex streamlit` runs lex-app's own `streamlit_app.py`, which imports
`<project>._streamlit_structure` and calls `main()`. Everything below that line
is yours: lex-app supplies identity, the theme, the logo and a way out, then
gets out of the way.

The app is organised by the thing being shown rather than by a task, because
each page is one capability you are likely to want:

    Overview          Streamlit's own widgets and lex-app's, in one layout
    The table         lex_view — the application's grid, embedded whole
    A narrower view   lex_view(serializer=…) — the same route, fewer columns
    Reacting          lex_view(on_select=…) — the event comes back to Python
    Calculations      lex_widgets — control, live log and execution tree

Kept to the shape a real dashboard has. An example that looks like nobody would
write it teaches the wrong thing.
"""

from __future__ import annotations

PAGES = (
    "Overview",
    "The table",
    "A narrower view",
    "Reacting to the table",
    "Calculations",
)


def main(user=None) -> None:
    import streamlit as st

    st.set_page_config(page_title="Northwind Analytics", layout="wide")
    page = st.sidebar.radio("Northwind Analytics", PAGES)
    st.sidebar.caption("A standalone Streamlit app, served by `lex streamlit`.")

    {
        "Overview": _overview,
        "The table": _table,
        "A narrower view": _narrower,
        "Reacting to the table": _reacting,
        "Calculations": _calculations,
    }[page]()


def _funds():
    from Input.Fund import Fund

    return list(Fund.objects.select_related("currency").order_by("name"))


def _valuation():
    from Reports.FundValuation import FundValuation

    return FundValuation.objects.order_by("pk").first()


# ── Overview ────────────────────────────────────────────────────────────────
def _overview() -> None:
    """Streamlit's own widgets and lex-app's, in one layout.

    The claim this page makes is that the two mix: `st.metric` and a real
    Calculate control sit in the same columns, and nothing about the page
    announces which is which.
    """
    import pandas as pd
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    st.title("Portfolio")
    st.caption("Positions and valuations across every active fund.")

    funds = _funds()
    if not funds:
        st.info("No funds yet. Create one in the app and this page fills in.")
        return

    a, b, c = st.columns(3)
    a.metric("Funds", len(funds))
    b.metric("Total NAV", f"{sum(float(f.nav or 0) for f in funds):,.0f}")
    c.metric("Active", sum(1 for f in funds if f.is_active))

    frame = pd.DataFrame(
        {"Fund": [f.name for f in funds], "NAV": [float(f.nav or 0) for f in funds]}
    ).set_index("Fund")
    st.bar_chart(frame["NAV"], height=240)

    valuation = _valuation()
    if valuation is None:
        return

    st.subheader("Revalue")
    st.write(
        "The control below is the one the record page uses. It is not a link to "
        "it — the calculation runs, reports its status and writes its log "
        "without leaving this page."
    )
    narrow, rest = st.columns([2, 5])
    with narrow:
        with lex_widgets(key="revalue") as block:
            block.calculation("fundvaluation", pk=valuation.pk, variant="action")
    with rest:
        st.write(
            "`lex_widgets()` opens one host for several controls. A single flat "
            "`lex_calculation(...)` call would do for one button."
        )


# ── lex_view, whole ─────────────────────────────────────────────────────────
def _table() -> None:
    """The application's own route, embedded.

    Not a copy of the grid: the same filters, the same saved views, the same
    export. `lex_view` frames the route and strips the chrome around it,
    because this page already has a sidebar of its own.
    """
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    st.title("The table")
    st.write(
        "`lex_view(\"fund\")` — the application's own table. Filter, group, sort "
        "and export it here exactly as you would there."
    )
    st.code('lex_view("fund", height=560)', language="python")
    lex_view("fund", height=560)


# ── lex_view, narrowed by a serializer ──────────────────────────────────────
def _narrower() -> None:
    """The same route, through a different serializer.

    This is the argument for `serializer=`: the embed is a *view* of the model,
    and a dashboard usually wants fewer columns than the application does. The
    narrowing happens on the server, so the columns the reader is not allowed
    to see are never sent.
    """
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    st.title("A narrower view")
    st.write(
        "The same route and the same data, asked for through the `summary` "
        "serializer the project registered on `Fund`. The framework's own "
        "audit columns are gone, the foreign key reads as a currency code, and "
        "the toolbar is hidden because this frame is for reading."
    )

    left, right = st.columns(2)
    with left:
        st.caption("What the project declared")
        st.code(
            'class FundSummarySerializer(serializers.ModelSerializer):\n'
            '    currency = serializers.CharField(\n'
            '        source="currency.code", read_only=True)\n\n'
            '    class Meta:\n'
            '        model = Fund\n'
            '        fields = ["id", "name", "currency",\n'
            '                  "nav", "strategy", "is_active"]\n\n'
            'Fund.api_serializers = {"summary": FundSummarySerializer}',
            language="python",
        )
    with right:
        st.caption("What the dashboard asks for")
        st.code(
            'lex_view(\n'
            '    "fund",\n'
            '    serializer="summary",\n'
            '    hide_toolbar=True,\n'
            '    hide_actions=True,\n'
            '    height=420,\n'
            ')',
            language="python",
        )

    lex_view("fund", serializer="summary", hide_toolbar=True, hide_actions=True, height=420)


# ── lex_view, bidirectional ─────────────────────────────────────────────────
def _reacting() -> None:
    """The embed talking back.

    With an `on_*` flag set, `lex_view` stops being an iframe and becomes a
    Streamlit component: the page re-runs when something happens in the table,
    and the call returns the event. Everything below it is evaluated again with
    that event in hand — which is why the panel on the right can be ordinary
    Streamlit code.
    """
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    st.title("Reacting to the table")
    st.write(
        "Select a row. The page re-runs and `lex_view(...)` returns the event, "
        "so the panel beside it is ordinary Streamlit reading an ordinary dict."
    )
    st.code(
        'event = lex_view("fund", on_select=True, on_update=True, height=380)\n'
        'if event and event["type"] == "select":\n'
        '    st.json(event["payload"])',
        language="python",
    )

    table, panel = st.columns([3, 2])
    with table:
        event = lex_view("fund", on_select=True, on_update=True, height=380, key="reactive")
    with panel:
        st.caption("What came back")
        if event:
            st.json(event)
        else:
            st.info(
                "Nothing yet — `lex_view` returns `None` until the first event. "
                "Guard on `event and event[\"type\"] == …`."
            )


# ── the widget family ───────────────────────────────────────────────────────
def _calculations() -> None:
    """Control, live log and execution tree — one host, three widgets.

    The page the widget documentation needed: the three members of the family
    side by side, in one `lex_widgets()` block, which is one iframe and one
    React runtime rather than three.
    """
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    st.title("Calculations")

    valuation = _valuation()
    if valuation is None:
        st.info("No valuation records yet.")
        return

    st.write(f"Valuation **#{valuation.pk}** — {valuation.fund}")
    st.code(
        'with lex_widgets(key="run") as page:\n'
        '    page.calculation("fundvaluation", pk=%d, title="Revalue")\n'
        '    page.calculation_log("fundvaluation", pk=%d, height=260)\n'
        '    page.calculation_log_tree("fundvaluation", pk=%d)' % (
            valuation.pk, valuation.pk, valuation.pk),
        language="python",
    )

    with lex_widgets(key="run", min_height=520) as page:
        page.calculation("fundvaluation", pk=valuation.pk, title="Revalue")
        page.calculation_log("fundvaluation", pk=valuation.pk, height=260)
        page.calculation_log_tree("fundvaluation", pk=valuation.pk)

    st.caption(
        "Widget count is free; block count is not. Three widgets in one block "
        "boot one React application — three flat calls would boot three."
    )
