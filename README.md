# Northwind Analytics

A small, complete Lex App project whose reason to exist is the **Streamlit
surface**: `lex_view`, `lex_widgets`, serializers, and the callbacks that let a
dashboard react to the grid embedded inside it.

Five funds, their positions, and one calculation that values a fund. Enough
data for every page to show something real, and little enough that the whole
project fits in your head.

## What it demonstrates

`_streamlit_structure.py` is the whole dashboard. Its sidebar has two levels,
and the first one is the distinction that matters most in this API — **which
way round the embedding goes**:

### Embedding app pages — `lex_view`

A lex-app route inside Streamlit.

| Page | Demonstrates |
|---|---|
| **A route, embedded** | `lex_view("fund")` — the application's grid, whole. Same filters, same saved views, same export. Plus every plain-embed argument: `hide_toolbar`, `hide_actions`, `height`, `width`, `scrolling`, `extra_params`, `base_url` |
| **Narrowing with a serializer** | `lex_view(serializer="summary")` — the same route through a second serializer. Fewer columns, chosen on the server |
| **Reacting to events** | All six `on_*` flags live, with the real envelope rendered beside the table, and a table of what each flag actually delivers |
| **Chaining forms with Flow** | `flow=` in both forms — a **mapping** of rules, and a **sequence** of steps with `as_`, `ref()`, and the endings — each shown with the JSON it serialises to |

### Embedding app controls — `lex_widgets`

A lex-app control inside Streamlit.

| Page | Demonstrates |
|---|---|
| **The three widgets** | `calculation`, `calculation_log`, `calculation_log_tree` in one block — one iframe, one React runtime |
| **Shaping a control** | Every argument `page.calculation()` takes, each rendered live: `variant` in all three forms, `title`, `fields`, `show_log`, `show_log_button` |
| **Reacting to a run** | `on_status=True` — the status envelope, and the rest of the page responding to a run finishing |
| **Layout and cost** | Width belongs to Streamlit; `min_height` is a floor, not a size; and why widget count is free but block count is not |

### On your models — `streamlit_main`

The other direction: Streamlit inside lex-app.

| Page | Demonstrates |
|---|---|
| **Record and table dashboards** | `streamlit_main` and `streamlit_class_main` — where each appears, and this project's own `Fund.streamlit_main` |

Every page follows the same four beats, so one page teaches you to read the
rest: **what it shows → the code → the live thing → what to notice.** Nothing
is mocked — the tables are the application's tables, the Calculate button is
the application's Calculate button, and the envelopes are the ones your own
dashboard will receive.

Two surfaces live on the models rather than in the dashboard:

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
├── _streamlit_structure.py     ← the dashboard: main() and its ten pages
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

**Keep `st.*` calls inside a function.** A module-level `st.title(...)` runs
when Django imports the model, before there is a page to draw into: it renders
nothing and logs `missing ScriptRunContext`. The *import* is not the problem —
`import streamlit as st` at the top of a model file is harmless, it only makes
every start-up pay for loading Streamlit. This project imports inside the
methods for that reason, not because the alternative breaks.

## Documentation

- [Streamlit dashboards](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/streamlit-dashboards) — the section, and what to read in order
- [Embedding app pages](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/lex_view-callbacks) — `lex_view`, its events and its flows
- [Embedding app controls](https://excellencecloudgmbh.github.io/lex-app-docs/access-and-dashboards/widgets) — `lex_widgets` and the flat `lex_*` calls
- [The TeamBudget tutorial](https://excellencecloudgmbh.github.io/lex-app-docs/start-here/tutorial/) — build a project from scratch
