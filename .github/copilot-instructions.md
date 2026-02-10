# Copilot Instructions for grid-game

## Project Overview

This is a **Dash educational game** simulating France's electricity grid balancing. Players build an energy mix and the app dispatches production hourly using merit order logic. The UI supports **French and English** with a flag toggle (🇫🇷/🇬🇧). All user-facing text is managed via `translations.py`.

## Tech Stack

- **Python 3.13** (see Dockerfile)
- **Dash** — UI framework (single-page app, HTTP callbacks, no WebSocket)
- **Plotly** — all charts (no matplotlib)
- **Pandas** — DataFrames for hourly production data
- **NumPy** — numerical arrays (demand curve, generation profiles)
- No database; all data is hardcoded in `data.py`

## File Responsibilities

| File                     | Role                                                                 |
| ------------------------ | -------------------------------------------------------------------- |
| `data.py`                | Static data only — energy source definitions, demand curve, profiles |
| `simulation.py`          | Pure computation — dispatch algorithm, KPI calculation, scoring      |
| `app.py`                 | Dash entry point — layout assembly, main callback                    |
| `components/sidebar.py`  | Slider controls and player choice conversion                         |
| `components/metrics.py`  | Metric cards, status messages, data table builders                   |
| `components/charts.py`   | All Plotly chart builder functions                                   |
| `components/welcome.py`  | Welcome screen and pedagogical section                               |
| `translations.py`        | i18n — FR/EN translation dictionaries, `t()` and `nom_source()`     |
| `assets/style.css`       | Dark theme CSS (auto-served by Dash)                                 |

**Strict separation**: `data.py` has no imports from other project files. `simulation.py` imports only from `data.py`. `translations.py` imports from `data.py` only (lazy, inside `nom_source()`). `components/` modules import from `data.py` and `translations.py`. `app.py` imports from `data.py`, `simulation.py`, `translations.py`, and `components/`.

## Key Data Structures

### `MOYENS_PRODUCTION` (dict in data.py)
Each energy source is a dict with these keys:
- `nom` (str): display name
- `emoji` (str): icon
- `couleur` (str): hex color for charts
- `cout_construction` (int): construction cost per unit in M€
- `cout_production` (int): marginal cost in €/MWh
- `disponibilite` (float): availability factor 0–1
- `co2` (int): emissions in gCO₂/kWh
- `puissance` (int): nominal power per unit in MW
- `pilotable` (bool): True = dispatchable, False = intermittent
- `max_unites` (int): maximum buildable units (slider max)
- `duree_vie` (int): lifespan in years (for LCOE amortization)
- `description` (str): educational description

### `DEMANDE_HORAIRE` (numpy array, 24 elements)
Hourly demand in MW. Index = hour of day (0–23). Typical French profile: night trough ~26 GW, evening peak ~58 GW.

### `choix_joueur` (dict)
Player's choices: `{source_id: nb_units, ...}` e.g. `{"nucleaire": 3, "solaire": 10}`.

### Production DataFrame (returned by `calculer_production_horaire`)
Columns: `heure`, `label`, `demande_mw`, one column per source (MW produced that hour), `production_totale`, `deficit`, `surplus`.

## Simulation Logic

### Merit Order Dispatch (2-pass per hour)
1. **Pass 1 — Non-dispatchable sources**: nuclear (constant at availability rate), solar (follows `PROFIL_SOLAIRE`), wind (follows `PROFIL_EOLIEN`). They produce everything they can regardless of demand.
2. **Pass 2 — Dispatchable sources**: hydro, coal, gas, oil — sorted by `cout_production` ascending. Each produces `min(available_capacity, remaining_demand)`.

### Scoring Formula (100 points max)
- **Coverage** (40 pts): linear 0→40 as coverage goes 80%→100%. Below 80% = 0.
- **CO₂** (30 pts): `30 × (1 − actual_co2 / reference_co2)` where reference = 100% coal.
- **Cost** (30 pts): `30 × (1 − LCOE / 80)` where 80 €/MWh is the gas reference.
- **Surplus penalty** (−25 max): `min(25, surplus_ratio × 50)`.

## Coding Conventions

- **Language**: variable names, comments, and docstrings are in **French**. All user-facing strings are in `translations.py` with FR/EN versions
- **i18n pattern**: every component function accepts a `lang` parameter (`"fr"` or `"en"`). Use `t(key, lang)` for static text and `nom_source(source_id, lang)` for energy source names. Never hardcode user-facing text in components
- **Naming**: snake_case throughout; source IDs are lowercase French: `nucleaire`, `hydraulique`, `eolien`, `solaire`, `charbon`, `gaz`, `petrole`
- **Units**: MW for power, MWh for energy, M€ for costs, gCO₂/kWh for emissions, tonnes for total CO₂
- **Charts**: always use `plotly_dark` template with transparent backgrounds (`rgba(0,0,0,0)`)
- **Colors**: primary blue `#00AAFF`, primary green `#A0D911`, dark background `#1B2A4A`. Each source has a fixed `couleur` in `MOYENS_PRODUCTION`
- **CSS**: custom classes (`metric-card`, `info-box`, `warning-box`, `success-box`, `metrics-row`, `charts-row`, etc.) defined in `assets/style.css` and used via `className` props on Dash `html.*` components

## Common Modification Scenarios

### Adding a new energy source
1. Add entry to `MOYENS_PRODUCTION` in `data.py` with all required keys
2. Add the source ID to `ORDRE_MERIT` list at the appropriate position (dispatch priority)
3. If intermittent, create a `PROFIL_<SOURCE>` numpy array (24 elements, 0–1) in `data.py` and add a condition in `calculer_production_horaire` pass 1
4. Add the English name to `NOMS_SOURCES_EN` in `translations.py`
5. No changes needed in `app.py` — it dynamically iterates over `ORDRE_MERIT`

### Changing the demand curve
Edit `DEMANDE_HORAIRE` in `data.py`. It's a 24-element numpy array of MW values, index = hour.

### Adjusting scoring weights
Edit `calculer_indicateurs` in `simulation.py`. Look for `score_couverture`, `score_co2`, `score_cout`, `malus_surplus` computations.

### Adding a new chart
1. Add a new builder function in `components/charts.py` returning a `go.Figure`. Use `_LAYOUT_COMMUN` dict for consistent styling.
2. In `app.py`, call the builder inside the `mettre_a_jour` callback and wrap in `dcc.Graph(figure=..., config={"displayModeBar": False})`.
3. Use source colors from `MOYENS_PRODUCTION[source_id]["couleur"]`.

### Adding storage / batteries
Would require a third dispatch pass in `calculer_production_horaire`: charge during surplus hours, discharge during deficit. Add `stockage` fields to data model.

## Testing Considerations

- There are currently **no automated tests**. When adding tests, use `pytest`.
- `simulation.py` functions are pure (input → output) and easy to unit test.
- Test edge cases: all sliders at 0, single source maxed out, 100% intermittent mix.
- Verify deficit/surplus calculations: `deficit + production_totale >= demande_mw` for all hours.

## Docker

- Base image: `python:3.13-slim`
- Entrypoint: `python app.py` on port 8501
- Health check: `curl http://localhost:8501/`
- No volumes or environment variables needed

## Dash-Specific Notes

- **No WebSocket**: Dash uses HTTP POST for all callbacks — firewall-friendly.
- **Callback pattern**: one main callback in `app.py` takes `lang-store` + 7 slider `Input`s and returns 7 `Output`s (content, title, subtitle, sidebar, invest, puissance, warning). Two clientside callbacks handle language button state.
- **`server = app.server`**: exposed for WSGI deployment (gunicorn, etc.).
- **Assets folder**: `assets/style.css` is auto-served by Dash at `/_dash-component-suites/`. No manual linking needed.
- **Chart config**: all `dcc.Graph` use `config={"displayModeBar": False}` to hide the Plotly toolbar.

## Internationalization (i18n)

- **Language store**: `dcc.Store(id="lang-store")` holds the current language (`"fr"` or `"en"`). Default is `"fr"`.
- **Flag toggle**: two `html.Button` elements (🇫🇷 / 🇬🇧) in `.lang-switcher` div, positioned top-right via CSS. A clientside callback updates the store instantly (no server round-trip).
- **Translation lookup**: `t(key, lang)` in `translations.py`. ~80 keys cover all UI text. `nom_source(source_id, lang)` translates energy source names.
- **Component pattern**: every component builder (`creer_sidebar`, `creer_metriques`, `graphique_*`, etc.) accepts a `lang` parameter. The main callback reads `lang-store` and passes it through.
- **Sidebar rebuild**: when language changes, the entire sidebar is rebuilt via `creer_sidebar(lang, choix_joueur)` which preserves current slider values.
- **Adding a translation**: add a new entry to `_TRADUCTIONS` dict in `translations.py` with `{"fr": ..., "en": ...}`, then use `t("new_key", lang)` in the component.
