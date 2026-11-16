# ROYAL INSIGHT
### Pressure Performance & Auction Intelligence Platform

An interactive analytics dashboard built on the **SupeRR Selector Season 2** analysis
(Rajasthan Royals IPL 2027 auction strategy). It reproduces - never re-invents - the exact
pressure model, player rankings and methodology from the original Round 1 submission, and
lets you explore them interactively instead of reading them off a static PDF.

---

## 1. Quick Start (Windows)

1. Extract this ZIP anywhere on your computer (e.g. `Desktop\Royal_Insight_Dashboard`).
2. Double-click **`run.bat`**.
3. On the first run, it will:
   - create a local Python virtual environment (`venv/`),
   - install the required packages (Streamlit, Plotly, Pandas, etc.),
   - launch the app, and
   - open it in your default browser at `http://localhost:8501`.
4. On every later run, steps 1-2 above are skipped automatically (it only re-installs
   packages if `requirements.txt` changes), so it starts in a few seconds.
5. To stop the app, just close the black command-window that `run.bat` opened.

**Requirements:** Python 3.10 or newer, installed with "Add python.exe to PATH" ticked
during setup (get it from [python.org/downloads](https://www.python.org/downloads/) if you
don't have it). No database, no API keys, no login, no manual configuration of any kind.

### Running it manually (any OS, e.g. macOS/Linux)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 2. What's Inside

| Page | What it shows |
|---|---|
| **Executive Overview** | Headline KPIs, pressure-tier mix, season coverage, top performers |
| **Pressure Analysis** | The exact pressure formula, interactive filters, delivery-level explanations |
| **Batter Analytics** | Full batting leaderboard, search/filter/sort, player drill-down, multi-player compare |
| **Bowler Analytics** | Full bowling leaderboard, search/filter/sort, player drill-down, multi-player compare |
| **Player Comparison** | Radar-chart + table comparison of any 2+ batters or 2+ bowlers |
| **RR Auction Intelligence** | Role-based recommendations for Rajasthan Royals, with a squad-fit matrix |
| **Match & Delivery Explorer** | Filterable, downloadable ball-by-ball table behind every number in the app |
| **Methodology & Transparency** | The full written methodology, in plain language, with live validation numbers |

## 3. Data & Model Accuracy

This dashboard **reads, it does not recompute**, the final analysis:

- `data/processed/deliveries_with_pressure.parquet` - the full ball-by-ball dataset with the
  Pressure Score already attached (same score used for the final rankings).
- `data/processed/batting_scores_full.csv` / `bowling_scores_full.csv` - the exact same
  player-level rankings behind `SupeRR_Player_Rankings.xlsx` and the final presentation.
- `data/*.csv` - the original supporting tables (matches, competitions, teams, playing XIs,
  player mappings) exactly as supplied in the SupeRR Selector data pack.
- `outputs/player_rankings.xlsx` - a copy of the final submitted rankings workbook.

Player IDs, player names, match IDs, competition IDs, the pressure definition, the scoring
weights, and the final Top-10 rankings are all unchanged from the original submission. If you
ever see a number here that looks different from the Excel file or the presentation, that is a
bug to report, not an intentional re-calculation - open an issue describing which page and
metric looked off.

**Why no raw `ball_by_ball.csv`?** The raw file is ~40 MB; the pre-processed parquet above is
the same information, already cleaned and with every derived pressure field attached, at a
fraction of the size (~8 MB) and much faster to load. Nothing in it was invented - it is a
direct, documented transformation of the original file (see the Methodology page for exactly
what was done).

## 4. Features Implemented

- 8 fully interactive pages (see table above), all reading live from the data files.
- Search, multi-select filters, and sortable leaderboards for both batters and bowlers.
- Player drill-down cards (phase breakdown, season trend) and multi-player comparison (radar
  charts + tables) for both disciplines.
- A filterable, exportable ball-by-ball "Match & Delivery Explorer" with a single-player
  situation breakdown.
- Role-based Rajasthan Royals auction shortlist with a visual squad-fit matrix.
- CSV download buttons on every leaderboard, comparison and explorer table.
- Cached data loading (`st.cache_data`) so filtering large tables stays fast.
- Clear empty-state messages when a filter/search returns nothing.
- "Last refreshed" / data-source caption on the Overview page.
- Dark navy / royal pink / gold "Royal Insight" visual theme, applied consistently via
  `assets/custom.css` and `.streamlit/config.toml`.

## 5. Known Limitations (by design, not bugs)

- No authentication/login - this is an internal analyst tool for local use; a login system
  would add friction with no real security benefit for a single-user local app. If your
  franchise later needs role-based access (e.g. scouts vs. decision-makers seeing different
  pages), that can be added with `streamlit-authenticator` without changing any of the
  underlying analysis - see Section 6.
- No live/online data feed - this is a point-in-time analysis of the supplied historical data
  pack, not a live match tracker.
- No auction price, retention, or purse data - none was supplied, and the dashboard never
  invents it (see the Methodology and Auction Intelligence pages).
- The underlying model's own limitations (non-striker run-out attribution, 1st-innings
  par-rate proxy, DLS handling, etc.) are disclosed in full on the Methodology page - the
  dashboard surfaces them rather than hiding them.

## 6. Deploying to Streamlit Community Cloud (later)

The app is already structured for this:

1. Push this folder to a GitHub repository (the `.gitignore` already excludes `venv/` and
   caches; `.streamlit/config.toml` is tracked on purpose so the theme carries over).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, and click "New app".
3. Point it at your repository, branch, and set the main file to `app.py`.
4. Click Deploy. No secrets, environment variables, or API keys are required.
5. The parquet/CSV files under `data/` are small enough to commit directly; if your
   repository has a file-size limit, consider Git LFS for `deliveries_with_pressure.parquet`
   (~8 MB - usually fine without LFS, but noted here for completeness).

All file paths in the code are relative (via `os.path`), so no Windows-specific paths will
break a cloud deployment.

## 7. Project Structure

```
Royal_Insight_Dashboard/
    run.bat                    <- double-click this on Windows
    app.py                     <- main Streamlit entry point / page router
    requirements.txt
    README.md
    .gitignore
    .streamlit/
        config.toml             <- Royal Insight theme colors
    data/
        matches.csv, competitions.csv, teams.csv,
        playing_eleven.csv, competition_team_player_mapping.csv
        processed/
            deliveries_with_pressure.parquet
            batting_scores_full.csv, bowling_scores_full.csv
            batting_top10.csv, bowling_top10.csv
            batting_bootstrap_ci.csv, bowling_bootstrap_ci.csv
            pressure_thresholds.json, validation_summary.json, audit_report.json
    modules/
        data_loader.py          <- cached data access
        pressure_model.py       <- methodology constants + explainers (read-only)
        batting_analytics.py
        bowling_analytics.py
        player_comparison.py
        auction_intelligence.py
        visualizations.py       <- shared Plotly theme + chart builders
    pages/
        overview.py, pressure_analysis.py, batter_analytics.py, bowler_analytics.py,
        player_comparison.py, auction_intelligence.py, match_explorer.py, methodology.py
    outputs/
        player_rankings.xlsx    <- copy of the final submitted rankings workbook
    assets/
        logo.png, custom.css
```

---

*Built on the SupeRR Selector Season 2 data pack. All statistics describe historical
pressure-situation performance only - they are not predictions, auction valuations, or
guarantees of player availability.*
