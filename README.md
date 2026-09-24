# Northwind Analytics

A small, complete Lex App project whose reason to exist is the **Streamlit
surface**: `lex_view`, `lex_widgets`, serializers, and the callbacks that let a
dashboard react to the grid embedded inside it.

Five funds, their positions, and one calculation that values a fund. Enough
data for every page to show something real, and little enough that the whole
project fits in your head.

## What it demonstrates

`_streamlit_structure.py` is the whole dashboard, and each page is one thing:

| Page | API | What it shows |
|---|---|---|
| **Overview** | `st.metric`, `st.bar_chart`, `lex_widgets` | Streamlit's own widgets and lex-app's in one layout, with nothing announcing which is which |
| **The table** | `lex_view("fund")` | The application's grid embedded whole — same filters, same saved views, same export |
| **A narrower view** | `lex_view(serializer="summary")` | The same route through a second serializer: fewer columns, chosen on the server |
| **Reacting to the table** | `lex_view(on_select=True)` | The embed stops being an iframe and becomes a component — select a row and the event comes back to Python |
| **Calculations** | `lex_widgets` | The control, the live log and the execution tree, in one block and therefore one React runtime |

Two more surfaces are worth pointing at:

- **`Fund.streamlit_main`** (`Input/Fund.py`) — a record-level dashboard. It is
  what the Analytics tab renders when you open a fund, with `self` bound to
  that record.
- **`FundSummarySerializer`** (`Input/Fund.py`) — registered as `summary`, which
  is what makes `lex_view(serializer="summary")` resolve. The narrowing happens
  on the server, so columns the audience should not see are never sent.

## Running it

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then fill it in — see the comments in the file
lex init                    # migrations, Keycloak sync, initial data
lex seed_northwind          # the funds, positions and one valuation
```

Then, in two terminals:

```bash
lex start                   # the application
```

```bash
lex streamlit               # the dashboard
```

> `lex streamlit` starts the Streamlit app **and** an authentication proxy in
> front of it. The proxy needs a reachable Keycloak — if `.env` is not filled
> in, it will fail on the first request while building an authorize-redirect.

## Layout

```
northwind/
├── lex_config.py               ← project settings (PROJECT_GROUPS)
├── model_structure.yaml        ← the sidebar
├── _streamlit_structure.py     ← the dashboard: main() and its five pages
├── Input/                      ← the domain
│   ├── Currency.py
│   ├── Fund.py                 ← + streamlit_main, + FundSummarySerializer
│   └── Position.py
└── Reports/
    └── FundValuation.py        ← a CalculationModel; calculate() writes a log
```

There is no `manage.py`, no `admin.py`, no `views.py` — the framework provides
what those did. Models go in ETL folders: `Upload/` for ingestion (this project
has none), `Input/` for the domain, `Reports/` for what is computed.

## Things worth copying

**A calculation should log.** `FundValuation.calculate()` writes a heading, a
table and a summary line. The Calculations page shows the live log, the
execution tree and the consolidated log side by side — a calculation that
writes nothing leaves all three correct and empty, which demonstrates the
plumbing rather than the feature.

**One `lex_widgets()` block is one iframe.** Three widgets inside one block
boot one React application; three flat `lex_calculation(...)` calls would boot
three. Widget count is free, block count is not.

**Import Streamlit inside the method, not at the top of the model file.** Your
models are imported by Django at startup, when Streamlit is not running.

## Documentation

- [Streamlit dashboards](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/streamlit-dashboards)
- [`lex_view` callbacks](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/lex_view-callbacks)
- [Widgets](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/widgets)
- [The TeamBudget tutorial](https://excellencecloudgmbh.github.io/lex-app-docs/start-here/tutorial/) — build a project from scratch
