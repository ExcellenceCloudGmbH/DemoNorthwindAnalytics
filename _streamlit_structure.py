"""Northwind Analytics — the Streamlit surface of a Lex App project.

`lex streamlit` runs lex-app's own `streamlit_app.py`, which imports
`<project>._streamlit_structure` and calls `main()`. Everything below that line
is yours: lex-app supplies identity, the theme, the logo and a way out, then
gets out of the way.

Organisation
------------
The sidebar has two levels, and the first one is the distinction that matters
most in this API — which way round the embedding goes:

    Start                     what this app is, and the shape of the API
    Embedding app pages       lex_view  — a lex-app ROUTE inside Streamlit
    Embedding app controls    lex_widgets — a lex-app CONTROL inside Streamlit
    On your models            streamlit_main — Streamlit inside LEX-APP

Every page below follows the same four beats, so one page teaches you how to
read the rest:

    what it shows  →  the code  →  the live thing  →  what to notice

Each page is one capability, demonstrated against this project's real data.
Nothing here is a mock: the tables are the application's tables, the Calculate
button is the application's Calculate button, and the event envelopes are the
ones your own dashboard will receive.
"""

from __future__ import annotations

# ── navigation ──────────────────────────────────────────────────────────────
# Two levels, because a flat list of nine pages hides the one distinction a
# reader needs to hold on to. The second level is ordered as a reading order,
# not alphabetically.
SECTIONS: dict[str, tuple[str, ...]] = {
    "Start": (
        "Overview",
    ),
    "Embedding app pages": (
        "A route, embedded",
        "Narrowing with a serializer",
        "Reacting to events",
        "Chaining forms with Flow",
    ),
    "Embedding app controls": (
        "The three widgets",
        "Shaping a control",
        "Reacting to a run",
        "Layout and cost",
    ),
    "On your models": (
        "Record and table dashboards",
    ),
}


def main(user=None) -> None:
    import streamlit as st

    st.set_page_config(page_title="Northwind Analytics", layout="wide")

    st.sidebar.title("Northwind Analytics")
    section = st.sidebar.radio("Section", tuple(SECTIONS), key="_section")
    page = st.sidebar.radio("Page", SECTIONS[section], key=f"_page_{section}")
    st.sidebar.caption("A standalone Streamlit app, served by `lex streamlit`.")

    PAGES[page]()


# ── shared page furniture ───────────────────────────────────────────────────
def _lead(title: str, shows: str) -> None:
    """Every page opens the same way: what it is, then what it shows."""
    import streamlit as st

    st.title(title)
    st.write(shows)


def _code(snippet: str) -> None:
    import streamlit as st

    st.code(snippet.strip("\n"), language="python")


def _notice(*points: str) -> None:
    """Close every page with what to take away, as bullets."""
    import streamlit as st

    st.divider()
    st.caption("**What to notice**")
    for point in points:
        st.caption(f"— {point}")


# ── data helpers ────────────────────────────────────────────────────────────
def _funds():
    from Input.Fund import Fund

    return list(Fund.objects.select_related("currency").order_by("name"))


def _valuation():
    from Reports.FundValuation import FundValuation

    return FundValuation.objects.order_by("pk").first()


def _needs(obj, what: str) -> bool:
    """Say plainly when a page cannot run, instead of rendering empty widgets."""
    import streamlit as st

    if obj:
        return False
    st.info(f"No {what} yet. Run `lex seed_northwind` and this page fills in.")
    return True


# ════════════════════════════════════════════════════════════════════════════
# Start
# ════════════════════════════════════════════════════════════════════════════
def _overview() -> None:
    """Streamlit's own widgets and lex-app's, in one layout."""
    import pandas as pd
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    _lead(
        "Overview",
        "Streamlit's widgets and lex-app's in the same columns. Nothing on this "
        "page announces which is which — that is the point.",
    )

    funds = _funds()
    if _needs(funds, "funds"):
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
    if valuation is not None:
        st.subheader("Revalue")
        narrow, rest = st.columns([2, 5])
        with narrow:
            with lex_widgets(key="overview_revalue") as block:
                block.calculation("fundvaluation", pk=valuation.pk, variant="action")
        with rest:
            st.write(
                "The button on the left is the application's own Calculate "
                "control, not a link to it. The metrics and the chart above "
                "are plain Streamlit."
            )

    st.divider()
    st.subheader("The API, in one table")
    st.write(
        "Three entry points, and which one you want is decided by *what* you "
        "are embedding rather than by how it looks:"
    )
    st.table(
        {
            "Call": ["lex_view(path)", "lex_calculation(model, pk)", "lex_widgets()"],
            "Embeds": ["one lex-app route", "one lex-app control", "several controls"],
            "Returns": [
                "None, or an event envelope with an on_* flag",
                "None, or a status envelope with on_status=True",
                "a page object; each control returns its own",
            ],
        }
    )
    _notice(
        "A flat `lex_*` call is always exactly one thing; `lex_widgets()` is the "
        "block form you reach for once a page has several.",
        "Every one of these is an iframe. Widget count is free, block count is not.",
    )


# ════════════════════════════════════════════════════════════════════════════
# Embedding app pages — lex_view
# ════════════════════════════════════════════════════════════════════════════
def _route() -> None:
    """lex_view with no flags: a plain embed of one route."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    _lead(
        "A route, embedded",
        "`lex_view(\"fund\")` renders the application's own table here. Filter, "
        "group, sort and export it exactly as you would in the app — the saved "
        "views are the same saved views, because this is the same component.",
    )
    _code('lex_view("fund", height=520)')
    lex_view("fund", height=520)

    st.subheader("What else the plain embed takes")
    st.table(
        {
            "Argument": [
                "hide_toolbar", "hide_actions", "height",
                "width", "scrolling", "extra_params", "base_url", "theme",
            ],
            "Effect": [
                "hides History / Analytics / Density / Views / sidebar toggle",
                "hides the Create, Refresh and Export bar",
                "iframe height in pixels (default 800)",
                "pixels or a CSS string (ignored once a callback flag is set)",
                "whether the frame scrolls (ignored once a callback flag is set)",
                "any extra query parameters, forwarded as-is",
                "override the frontend URL for this call only",
                "superseded — the embed follows the host page's light/dark mode",
            ],
        }
    )
    _notice(
        "With no `on_*` flag this is `components.iframe` and returns `None`. "
        "Nothing about an existing plain embed changes when the callback "
        "feature is available.",
        "A leading `/` is added for you, so `\"fund\"` and `\"/fund\"` are the same "
        "route. `\"fund/42\"` opens one record; `\"fund/create\"` opens the form.",
    )


def _serializer() -> None:
    """lex_view(serializer=...): the same route, shaped by a second serializer."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    _lead(
        "Narrowing with a serializer",
        "An embed is a *view* of the model, and a dashboard usually wants fewer "
        "columns than the application does. `serializer=` names a serializer "
        "registered on the model, and the narrowing happens on the server — so "
        "the columns this audience should not see are never sent to the browser.",
    )

    left, right = st.columns(2)
    with left:
        st.caption("What the project declared — `Input/Fund.py`")
        _code(
            '''
class FundSummarySerializer(serializers.ModelSerializer):
    currency = serializers.CharField(
        source="currency.code", read_only=True)

    class Meta:
        model = Fund
        fields = ["id", "name", "currency",
                  "nav", "strategy", "is_active"]


Fund.api_serializers = {"summary": FundSummarySerializer}
'''
        )
    with right:
        st.caption("What the dashboard asks for")
        _code(
            '''
lex_view(
    "fund",
    serializer="summary",
    hide_toolbar=True,
    hide_actions=True,
    height=420,
)
'''
        )

    lex_view(
        "fund", serializer="summary",
        hide_toolbar=True, hide_actions=True, height=420, key="narrow",
    )
    _notice(
        "The framework's own audit columns are gone and the foreign key reads "
        "as a currency code, because that is what the serializer declares.",
        "An unregistered name is an HTTP 400 with the available keys listed — "
        "not a silent fall back to the default serializer.",
        "`serializer=` on its own does **not** switch to the bidirectional "
        "component. Only an `on_*` flag does that.",
    )


def _events() -> None:
    """The six on_* flags, and the envelope each one really delivers."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_view

    _lead(
        "Reacting to events",
        "Set any `on_*` flag and `lex_view` stops being an iframe: it becomes a "
        "Streamlit component, and the call returns the latest **event envelope**. "
        "Act in the table below and the panel beside it fills in.",
    )
    _code(
        '''
event = lex_view(
    "fund",
    on_select=True, on_create=True, on_update=True,
    on_delete=True, on_navigate=True,
    height=420,
)

if event and event["type"] == "select":
    st.write("Selected:", event["payload"]["ids"])
'''
    )

    table, panel = st.columns([3, 2])
    with table:
        event = lex_view(
            "fund",
            on_select=True, on_create=True, on_update=True,
            on_delete=True, on_navigate=True,
            height=420, key="events",
        )
    with panel:
        st.caption("The envelope that came back")
        if event:
            st.json(event)
        else:
            st.info(
                "Nothing yet. `lex_view` returns `None` until the first event, "
                "which is why every handler starts `if event and ...`."
            )

    st.subheader("The envelope")
    st.write(
        "Every event has the same outer shape. `type` and `payload` are what you "
        "read; `id` is what stops a re-run delivering the same event twice."
    )
    st.table(
        {
            "Key": ["type", "payload", "id", "ts", "source", "version"],
            "Meaning": [
                "the event kind — see the table below",
                "type-specific data",
                "unique per event; used to de-duplicate re-runs",
                "milliseconds since the epoch, set by the browser",
                'always "lex-app"',
                "the bridge protocol version",
            ],
        }
    )

    st.subheader("What each flag delivers")
    st.write("Read from the frontend that emits them, not from the flag names:")
    st.table(
        {
            "Flag": [
                "on_create", "on_update", "on_delete",
                "on_select", "on_navigate", "on_flow_step",
            ],
            "type": [
                "create", "update", "delete",
                "select", "navigate", "— never arrives —",
            ],
            "payload": [
                "resource, id, data",
                "resource, id, data",
                "resource, id",
                "resource, ids",
                "from, to",
                "nothing is emitted for this type",
            ],
            "Fires when": [
                "a create form saves",
                "an edit form saves",
                "a record is deleted from the edit toolbar",
                "the grid selection changes (debounced 150 ms)",
                "the embedded app routes somewhere else",
                "setting it only switches on bidirectional mode",
            ],
        }
    )
    st.warning(
        "`on_flow_step` is accepted and forwarded, but no `flow_step` event is "
        "emitted today — a handler guarded on it never runs. Flows themselves "
        "work: the routing happens inside the embedded app and needs no event. "
        "To observe a flow's progress, use `on_create` / `on_update`, which fire "
        "at each step that saves.",
        icon="⚠️",
    )
    _notice(
        "`data` on a create or update is the whole saved record as the API "
        "returned it — not just the id.",
        "`on_select` is opt-in for a reason: it re-runs your script on every "
        "selection change. The grid's selection callback is only wired when you "
        "ask for it.",
        "Every flag is gated at the source. Without the flag the embedded app "
        "does not emit, so an unused event costs nothing.",
    )


def _flows() -> None:
    """flow=: routing the user from one form to the next."""
    import streamlit as st

    from lex.lex_app.streamlit import STAY, Flow, lex_view, ref

    _lead(
        "Chaining forms with Flow",
        "`flow=` decides where the embedded app goes after a save. It has two "
        "forms, and they answer different questions — a **mapping** says \"after "
        "any X is created, go here\"; a **sequence** says \"do these, in this "
        "order\".",
    )

    st.subheader("A mapping: rules that fire wherever the user is")
    _code(
        '''
flow = (
    Flow()
    .after_create("fund", "/position/create")
    .after_update("position", STAY)      # clear the form, stay put
)

lex_view("fund", on_create=True, flow=flow)
'''
    )
    mapping = (
        Flow()
        .after_create("fund", "/position/create")
        .after_update("position", STAY)
    )
    st.caption("What that serialises to, on the wire")
    st.json(mapping.to_wire())

    st.divider()
    st.subheader("A sequence: steps with a position")
    st.write(
        "A mapping has no order in it, so it cannot express *first* this, "
        "*then* that, nor repeat one key, nor point back at an earlier step. "
        "The same `Flow` object, a different set of methods:"
    )
    _code(
        '''
flow = (
    Flow()
    .create("fund", as_="f")      # name it, to come back to it later
    .create("position")           # no id needed — follows the step before
    .update("fund", id=ref("f"))  # the fund step 1 made
    .table("fund")                # the ending
)

lex_view("fund", on_create=True, flow=flow)
'''
    )
    sequence = (
        Flow()
        .create("fund", as_="f")
        .create("position")
        .update("fund", id=ref("f"))
        .table("fund")
    )
    left, right = st.columns([2, 3])
    with left:
        st.caption("`flow.is_program`")
        st.write(sequence.is_program)
        st.caption("A mapping's")
        st.write(mapping.is_program)
    with right:
        st.caption("What the sequence serialises to")
        st.json(sequence.to_wire())

    st.subheader("Steps and endings")
    st.table(
        {
            "Method": [
                ".create(resource, as_=…)", ".update(resource, id=…, as_=…)",
                ".goto(path)", ".table(resource=None)", ".show(resource, id)",
                ".end_goto(path)", ".loop()", ".loop_last()",
            ],
            "Kind": ["step", "step", "step", "ending", "ending", "ending", "ending", "ending"],
            "Opens": [
                "the create form",
                "the edit form for one record",
                "any route; {id} and {resource} interpolate",
                "the table — defaults to the last step's resource",
                "one record's detail page",
                "any route",
                "start again from the first step",
                "repeat the final step",
            ],
        }
    )
    _notice(
        "`update` takes an id three ways: omitted (the record the previous step "
        "produced), a literal, or `ref(\"name\")` for a step you named with `as_`.",
        "References point backwards only. `ref()` for a step not yet written "
        "raises `FlowError` where you wrote it, not at run time.",
        "The two forms cannot be mixed — adding a step to a flow that holds "
        "mapping rules raises `FlowError`, and so does adding anything after an "
        "ending.",
        "`loop()` clears the bindings on each pass, so a `ref` cannot reach back "
        "into the previous lap. `loop_last()` is `STAY` with a cursor that does "
        "not move.",
    )


# ════════════════════════════════════════════════════════════════════════════
# Embedding app controls — lex_widgets
# ════════════════════════════════════════════════════════════════════════════
def _widgets() -> None:
    """The three widget types, in one block."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    _lead(
        "The three widgets",
        "A dashboard can host the application's own controls — not a "
        "re-implementation, the real control wired to the real record, with the "
        "same status, the same live log and the same permissions as the grid.",
    )

    valuation = _valuation()
    if _needs(valuation, "valuation records"):
        return

    st.write(f"Valuation **#{valuation.pk}** — {valuation.fund}")
    _code(
        f'''
with lex_widgets(key="run", min_height=520) as page:
    page.calculation("fundvaluation", pk={valuation.pk}, title="Revalue")
    page.calculation_log("fundvaluation", pk={valuation.pk}, height=260)
    page.calculation_log_tree("fundvaluation", pk={valuation.pk})
'''
    )
    with lex_widgets(key="run", min_height=520) as page:
        page.calculation("fundvaluation", pk=valuation.pk, title="Revalue")
        page.calculation_log("fundvaluation", pk=valuation.pk, height=260)
        page.calculation_log_tree("fundvaluation", pk=valuation.pk)

    st.table(
        {
            "Widget": [
                "calculation", "calculation_log", "calculation_log_tree",
            ],
            "Renders": [
                "the Calculate control: status pill, button, log button",
                "the calculation log as a live stream",
                "the finished run's execution tree",
            ],
            "Answers": [
                "can I run this, and what happened last time?",
                "what is happening right now?",
                "how was a completed run structured?",
            ],
        }
    )
    _notice(
        "The stream and the tree answer different questions. Reach for the "
        "stream while you are watching, the tree when navigating something that "
        "already finished.",
        "Each widget also has a flat one-call form — `lex_calculation`, "
        "`lex_calculation_log`, `lex_calculation_log_tree` — for when a page "
        "wants exactly one.",
    )


def _shaping() -> None:
    """Every argument page.calculation() takes, rendered."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    _lead(
        "Shaping a control",
        "`page.calculation()` is composable, and **absence means hidden**. The "
        "default is minimal; you add what a layout needs. Every variant below is "
        "live — they are the same widget with different arguments.",
    )

    valuation = _valuation()
    if _needs(valuation, "valuation records"):
        return
    pk = valuation.pk

    st.table(
        {
            "Argument": [
                "variant", "title", "fields", "show_log", "show_log_button", "on_status",
            ],
            "Effect": [
                '"full" (pill + button), "status" (pill alone), "action" (button alone)',
                "a heading above the control; omit it and none renders",
                "record fields beside the control, drawn by the app's own field renderer",
                "put the log inline under the control",
                "the button that opens the live log popup — on by default",
                "return the latest status envelope instead of None",
            ],
        }
    )

    st.subheader("full — the default")
    _code(f'page.calculation("fundvaluation", pk={pk})')
    with lex_widgets(key="shape_full") as page:
        page.calculation("fundvaluation", pk=pk)

    st.subheader("action — the button alone")
    _code(
        f'page.calculation("fundvaluation", pk={pk}, variant="action",\n'
        f'                 show_log_button=False)'
    )
    with lex_widgets(key="shape_action") as page:
        page.calculation("fundvaluation", pk=pk, variant="action", show_log_button=False)

    st.subheader("status — the pill alone, for a compact strip")
    _code(
        f'page.calculation("fundvaluation", pk={pk}, variant="status",\n'
        f'                 show_log_button=False)'
    )
    with lex_widgets(key="shape_status") as page:
        page.calculation("fundvaluation", pk=pk, variant="status", show_log_button=False)

    st.subheader("title and fields — the record beside the control")
    _code(
        f'page.calculation("fundvaluation", pk={pk}, title="Net asset value",\n'
        f'                 fields=["fund", "total_market_value"])'
    )
    with lex_widgets(key="shape_fields") as page:
        page.calculation(
            "fundvaluation", pk=pk,
            title="Net asset value", fields=["fund", "total_market_value"],
        )

    _notice(
        "`fields` are drawn by the application's own field renderer, so a "
        "foreign key shows its display name and a datetime is formatted as the "
        "grid formats it.",
        "A malformed spec raises `WidgetSpecError` at the call line — a "
        "misspelled option, an unknown variant, `fields` as a bare string. It "
        "raises rather than rendering blank, because a blank frame looks like a "
        "loading state and gets waited on.",
        "A model or pk that does not *exist* is different: that widget renders "
        "an error card and its siblings keep working.",
    )


def _on_status() -> None:
    """on_status=True: the rest of the page responds to a run finishing."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    _lead(
        "Reacting to a run",
        "With `on_status=True` the control returns the latest status envelope, "
        "so the rest of the page can respond to a calculation finishing. Press "
        "Calculate and watch the panel below it.",
    )

    valuation = _valuation()
    if _needs(valuation, "valuation records"):
        return

    _code(
        f'''
with lex_widgets(key="watch") as page:
    status = page.calculation("fundvaluation", pk={valuation.pk},
                              title="Revalue", on_status=True)

if status and status["payload"]["status"] == "SUCCESS":
    st.success("Recalculated — the figures below are current.")
'''
    )
    with lex_widgets(key="watch") as page:
        status = page.calculation(
            "fundvaluation", pk=valuation.pk, title="Revalue", on_status=True,
        )

    if status:
        st.caption("The status envelope")
        st.json(status)
        if status["payload"]["status"] == "SUCCESS":
            st.success("Recalculated — the figures below are current.")
    else:
        st.info("No status yet. Press Calculate above.")

    st.table(
        {
            "Key": ["type", "id", "payload.widget_id", "payload.model", "payload.pk", "payload.status"],
            "Meaning": [
                '"calculation_status" — worth checking, see below',
                "unique per event, used to de-duplicate re-runs",
                "which widget this is about, when a block has several",
                "the model the widget is wired to",
                "the record's primary key",
                "SUCCESS, ERROR, IN_PROGRESS, and the rest of the state machine",
            ],
        }
    )
    _notice(
        "Check `type` first. Every envelope type shares one component value, so "
        "a click on the log button arrives here too — and its payload has no "
        "`status` key.",
        "It arrives on the **next** re-run, not during the one that started the "
        "run. That is the contract every Streamlit input widget has.",
        "Status is opt-in per widget: only a `calculation` with `on_status=True` "
        "emits. A log widget emits nothing.",
    )


def _layout() -> None:
    """Width, min_height, and the one number that matters."""
    import streamlit as st

    from lex.lex_app.streamlit import lex_widgets

    _lead(
        "Layout and cost",
        "Two things to know before a page has many controls: widgets do not "
        "choose their own width, and the block you put them in is what costs.",
    )

    valuation = _valuation()
    if _needs(valuation, "valuation records"):
        return
    pk = valuation.pk

    st.subheader("Width belongs to Streamlit")
    st.write(
        "A custom component occupies a full-width block, so even a lone button "
        "spans the page. Constrain it the way you would any Streamlit element:"
    )
    _code(
        f'''
narrow, rest = st.columns([1, 6])
with narrow:
    with lex_widgets(key="run") as page:
        page.calculation("fundvaluation", pk={pk}, variant="action",
                         show_log_button=False)
with rest:
    st.write("… your own content, beside the button …")
'''
    )
    narrow, rest = st.columns([1, 6])
    with narrow:
        with lex_widgets(key="layout_narrow") as page:
            page.calculation("fundvaluation", pk=pk, variant="action", show_log_button=False)
    with rest:
        st.write("… your own content, beside the button …")

    st.divider()
    st.subheader("Widget count is free. Block count is not.")
    st.write(
        "Each `lex_widgets()` block is one iframe, and each iframe is a full "
        "React application: its own bundle parse, its own auth handshake, its "
        "own `model_info` fetch. Ten widgets in one block boot one app; ten "
        "blocks boot ten, and they contend for the same network and main thread."
    )
    good, bad = st.columns(2)
    with good:
        st.caption("✅ one runtime")
        _code(
            '''
with lex_widgets() as page:
    for pk in pks:
        page.calculation("fundvaluation", pk=pk)
'''
        )
    with bad:
        st.caption("❌ one runtime each")
        _code(
            '''
for pk in pks:
    lex_calculation("fundvaluation", pk=pk)
'''
        )

    _notice(
        "The cost of the block form, stated plainly: widgets appear where the "
        "`with` block closes, not where each call sits. You cannot interleave "
        "`st.write()` between two widgets in one block.",
        "Reach for a second block only when a layout genuinely needs Streamlit "
        "content between two groups. That is a real reason, and it costs a runtime.",
        "`min_height` is a floor, not a size — the height used before the host "
        "reports what it actually needs. Raise it only to avoid an initial reflow.",
        "`key` distinguishes two blocks on one page. Without it, two blocks read "
        "and write the same slot.",
    )


# ════════════════════════════════════════════════════════════════════════════
# On your models — the other direction
# ════════════════════════════════════════════════════════════════════════════
def _model_dashboards() -> None:
    """streamlit_main / streamlit_class_main — Streamlit inside lex-app."""
    import streamlit as st

    _lead(
        "Record and table dashboards",
        "Everything else in this app embeds lex-app inside Streamlit. These two "
        "go the other way: you write a method on a model, and the *application* "
        "decides when to show it. No routing, no separate app.",
    )

    st.table(
        {
            "Method": ["streamlit_main(self, user=None)", "streamlit_class_main(cls)"],
            "Receives": ["one record", "the model class"],
            "Appears": [
                "the Analytics tab on the record page",
                "the chart icon on the grid toolbar",
            ],
            "Use for": [
                "this record's detail — its positions, its history, a drill-down",
                "aggregates — summaries and charts across every record",
            ],
        }
    )

    st.subheader("This project's own — `Input/Fund.py`")
    st.write(
        "Open any fund in the application and its Analytics tab renders exactly "
        "this, with `self` bound to that fund:"
    )
    _code(
        '''
class Fund(LexModel):
    ...

    def streamlit_main(self, user=None):
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

        valuation = self.valuations.first()
        if valuation is not None:
            lex_calculation("fundvaluation", pk=valuation.pk)
'''
    )
    _notice(
        "The two directions compose: a record-level dashboard can itself embed "
        "a control, which is what the last three lines above do.",
        "One Streamlit process serves all three kinds. The query string decides: "
        "`?model=fund&pk=42` is record-level, `?model=fund` is table-level, and "
        "neither is this standalone app.",
        "A top-level `import streamlit as st` in a model file is harmless — it "
        "just makes every Django start-up load Streamlit. What does not work is "
        "an `st.*` **call** outside a function: it runs at import, before there "
        "is a page to draw into, and renders nothing.",
    )


PAGES = {
    "Overview": _overview,
    "A route, embedded": _route,
    "Narrowing with a serializer": _serializer,
    "Reacting to events": _events,
    "Chaining forms with Flow": _flows,
    "The three widgets": _widgets,
    "Shaping a control": _shaping,
    "Reacting to a run": _on_status,
    "Layout and cost": _layout,
    "Record and table dashboards": _model_dashboards,
}
