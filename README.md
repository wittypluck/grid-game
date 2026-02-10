# ⚡ Équilibre du Réseau Électrique

An educational web game where players build an electricity generation mix to cover France's 24-hour demand. Balance cost, CO₂ emissions, and supply reliability to achieve the best score.

![Python 3.13](https://img.shields.io/badge/python-3.13-blue)
![Dash](https://img.shields.io/badge/dash-latest-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Players choose how many power plants of each type to build (nuclear, hydro, solar, wind, coal, gas, oil), and the simulation dispatches production hour by hour using a **merit order** algorithm — the same principle used on real European electricity markets.

The game illustrates real-world energy challenges:

- **Intermittency** — solar and wind produce only when weather allows, not on demand
- **Base load vs. peak** — nuclear provides steady output, gas handles peaks
- **Cost vs. emissions** — fossil fuels are flexible but polluting; renewables are clean but variable
- **Supply-demand balance** — deficit = blackout, surplus = waste

## Scoring

The player's mix is scored out of 100 points:

| Criterion         | Max points | Description                                              |
| ------------------ | ---------- | -------------------------------------------------------- |
| Demand coverage    | 40         | 100% coverage required for full marks; 0 below 80%      |
| CO₂ emissions      | 30         | Compared to a 100% coal reference scenario               |
| Cost (LCOE)        | 30         | Amortized cost per MWh vs. an 80 €/MWh gas reference     |
| Surplus penalty    | −25 max    | Overproduction is penalized proportionally               |

## Architecture

```
grid-game/
├── app.py                  # Dash entry point — layout & main callback
├── data.py                 # Data model — energy sources, demand curve, profiles
├── simulation.py           # Simulation engine — dispatch, KPIs, scoring
├── translations.py         # i18n — FR/EN translation dictionaries & helpers
├── components/             # UI components (one module per concern)
│   ├── __init__.py
│   ├── sidebar.py          # Slider controls & player choices
│   ├── metrics.py          # Metric cards, status messages, data tables
│   ├── charts.py           # All Plotly chart builders
│   └── welcome.py          # Welcome screen & pedagogical section
├── assets/
│   └── style.css           # Dark theme stylesheet (auto-loaded by Dash)
├── requirements.txt
└── Dockerfile
```

### data.py — Data Model

Defines the energy system parameters:

- **`MOYENS_PRODUCTION`** — dictionary of 7 energy sources, each with: nominal power (MW), construction cost (M€), marginal production cost (€/MWh), CO₂ intensity (gCO₂/kWh), availability factor, dispatchability flag, max units, and lifespan
- **`DEMANDE_HORAIRE`** — 24-element NumPy array representing France's typical daily load curve (26–58 GW), with a morning peak at 09h and an evening peak at 19h
- **`PROFIL_SOLAIRE` / `PROFIL_EOLIEN`** — hourly capacity factor profiles for intermittent sources (solar peaks at 13h, wind is higher at night)
- **`ORDRE_MERIT`** — ordered list defining the dispatch priority

### simulation.py — Simulation Engine

Two main functions:

- **`calculer_production_horaire(choix_joueur)`** — runs the hourly dispatch in two passes:
  1. **Non-dispatchable sources** (nuclear, solar, wind) produce at their available capacity
  2. **Dispatchable sources** (hydro, gas, coal, oil) fill the remaining gap in merit order (cheapest first)
  
  Returns a DataFrame with hourly production per source, total, deficit, and surplus.

- **`calculer_indicateurs(choix_joueur, df_production)`** — computes KPIs: construction cost, production cost, LCOE (amortized), CO₂ emissions, coverage rate, composite score.

### translations.py — Internationalization (i18n)

Central translation module providing bilingual support (French / English):

- **`t(key, lang)`** — looks up a translation key and returns the string in the requested language (`"fr"` or `"en"`), with French fallback
- **`nom_source(source_id, lang)`** — returns the display name of an energy source in the requested language
- **`NOMS_SOURCES_EN`** — mapping of source IDs to English names (Coal, Natural Gas, Oil, Nuclear, Hydro, Solar, Wind)
- ~80 translation keys covering all UI text: titles, sidebar labels, metric cards, status messages, chart axes/legends/hover templates, welcome screen, pedagogical guide, table headers, and footer

### app.py + components/ — Dash UI

The UI layer is built with **Dash** (HTTP-only, no WebSocket) and split into focused modules:

- **`app.py`** — Dash app initialization, layout assembly, language toggle (🇫🇷/🇬🇧 flags via `dcc.Store` + clientside callbacks), and main callback (wires slider inputs + language to all outputs)
- **`components/sidebar.py`** — builds sidebar with 7 sliders + summary; `lire_choix_joueur()` converts slider values to game dict; accepts `lang` and `valeurs` to preserve slider state across language switches
- **`components/metrics.py`** — metric card generation, status messages (success/warning/alert), data table helpers — all accept `lang` for translated labels
- **`components/charts.py`** — all 6 Plotly chart builders (production stack, demand curve, pie chart, score bars, cost bars, CO₂ bars) — axis titles, legends, and hover templates translated via `lang`
- **`components/welcome.py`** — welcome screen layout and pedagogical accordion — fully translated
- **`assets/style.css`** — dark theme CSS (auto-served by Dash from the `assets/` folder), includes language switcher styling

Custom dark theme with Engie-inspired color scheme (blue `#00AAFF` / green `#A0D911`)

## Getting Started

### Prerequisites

- Python 3.10+ (developed with 3.13)
- pip

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

### Docker

```bash
# Build
docker build -t grid-game .

# Run
docker run -p 8501:8501 grid-game
```

## Dependencies

| Package    | Purpose                          |
| ---------- | -------------------------------- |
| dash       | Web application framework (HTTP callbacks, no WebSocket) |
| plotly     | Interactive charts               |
| pandas     | Data manipulation (DataFrames)   |
| numpy      | Numerical arrays and computation |

## How the Simulation Works

1. The player selects units for each energy source via sidebar sliders
2. For each of the 24 hours:
   - Non-dispatchable sources produce at their weather-dependent capacity factor
   - Remaining demand is filled by dispatchable sources in increasing cost order
   - Any unmet demand is recorded as **deficit** (blackout)
   - Any excess production is recorded as **surplus** (waste)
3. KPIs are computed: total cost (construction + production), CO₂, LCOE, coverage %
4. A composite score (0–100) is calculated based on coverage, emissions, cost, and surplus penalty
5. Results are displayed via interactive Plotly charts and metric cards

## Key Concepts for Players

- **Merit order**: power plants are called in order of marginal cost — renewables and nuclear first, then gas, coal, oil last
- **Dispatchable vs. intermittent**: dispatchable sources (hydro, gas, coal, oil) can adjust output; intermittent sources (solar, wind, nuclear*) cannot
- **LCOE**: Levelized Cost of Electricity — construction cost amortized over the plant's lifespan, plus operating costs, divided by energy produced

> *Nuclear is modeled as non-dispatchable in this simulation to reflect its operational inertia (slow ramping), which is a simplification for educational purposes.

## Language

The application supports **French** and **English**. A language toggle (🇫🇷 / 🇬🇧 flag buttons) is located in the top-right corner of the main content area. All UI text — titles, labels, metric cards, chart axes and hover text, status messages, the welcome screen, and the pedagogical guide — switches instantly when a flag is clicked. The default language is French.

Code comments, variable names, and internal identifiers use French terminology. Translations are centralized in `translations.py`.
