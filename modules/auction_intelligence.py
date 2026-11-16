"""
Royal Insight - Rajasthan Royals Auction Intelligence.
Role tags below are the same squad-fit mapping used in the Round 1
presentation (built from each shortlisted player's phase-level pressure
profile - batting order / phase strike rate for batters, phase economy and
bowling style for bowlers). Nothing here invents prices, availability,
retentions or purse - those were never supplied and are explicitly out of
scope.
"""
from __future__ import annotations
import pandas as pd
from modules.data_loader import load_batting_top10, load_bowling_top10

BAT_ROLES = {
    "Jos Buttler": ["Top-order stability", "Middle-order acceleration", "Finishing"],
    "Tristan Stubbs": ["Middle-order acceleration", "Finishing"],
    "Sikandar Raza": ["Middle-order acceleration", "All-round flexibility"],
    "Cooper Connolly": ["Middle-order acceleration", "Finishing", "All-round flexibility"],
    "Rinku Singh": ["Finishing"],
    "Towhid Hridoy": ["Middle-order acceleration"],
    "Dion Myers": ["Middle-order acceleration", "Finishing"],
    "Mohammad Nabi": ["Finishing", "All-round flexibility"],
    "Gareth Delany": ["Finishing", "All-round flexibility"],
    "Jaker Ali Anik": ["Finishing"],
}

BOWL_ROLES = {
    "Kagiso Rabada": ["Powerplay bowling", "Death-over execution", "Pace variations"],
    "Umran Malik": ["Death-over execution", "Pace variations"],
    "Mustafizur Rahman": ["Middle-over wicket-taking", "Death-over execution", "Pace variations"],
    "Mohit Sharma": ["Powerplay bowling", "Death-over execution", "Pace variations"],
    "Nitish Reddy": ["Death-over execution", "All-round flexibility"],
    "Junaid Siddique": ["Middle-over wicket-taking", "Pace variations"],
    "Yuzvendra Chahal": ["Middle-over wicket-taking", "Spin options"],
    "Shadab Khan": ["Powerplay bowling", "Middle-over wicket-taking", "Spin options", "All-round flexibility"],
    "Abrar Ahmed": ["Middle-over wicket-taking", "Spin options"],
    "Mohammad Nawaz": ["Middle-over wicket-taking", "Spin options", "All-round flexibility"],
}

ALL_ROLES = [
    "Top-order stability", "Middle-order acceleration", "Finishing", "Powerplay bowling",
    "Middle-over wicket-taking", "Death-over execution", "Spin options", "Pace variations",
    "All-round flexibility",
]

REASONS = {
    "Jos Buttler": "Biggest pressure strike-rate uplift among top-order options (+44% vs. baseline) - proven finisher/opener dual threat.",
    "Tristan Stubbs": "Largest, most reliable sample of any batter (262 pressure balls) with a +28% SR gain and strong boundary rate.",
    "Sikandar Raza": "Consistent accelerator across IPL and T20I pressure situations with all-round utility.",
    "Cooper Connolly": "Elite pressure strike rate (210) with genuine all-round (bat + part-time bowling) flexibility.",
    "Rinku Singh": "Large sample (258 balls), proven IPL finisher archetype with high pressure strike rate.",
    "Towhid Hridoy": "Reliable middle-order accelerator with a solid pressure sample size.",
    "Dion Myers": "High pressure SR uplift, though smaller sample - a provisional, high-upside option.",
    "Mohammad Nabi": "Veteran finisher with all-round value and consistent pressure numbers.",
    "Gareth Delany": "Top-ranked batting score; explosive finisher profile, though lower sample size (132 balls).",
    "Jaker Ali Anik": "Strong finishing numbers in T20I cricket with a reasonable sample size.",
    "Kagiso Rabada": "Cuts economy under pressure across BOTH powerplay and death overs - rare two-way value.",
    "Umran Malik": "Highest bowling reliability score; economy drops sharply (9.9 -> 6.7) under pressure.",
    "Mustafizur Rahman": "Largest bowling sample (317 balls) with consistent death-overs pressure performance.",
    "Mohit Sharma": "Cheaper under pressure across powerplay and death, with a large, reliable sample.",
    "Nitish Reddy": "All-round death-bowling option that gets cheaper under pressure.",
    "Junaid Siddique": "Strong pressure economy improvement, though smaller sample (54 balls) - provisional pick.",
    "Yuzvendra Chahal": "Largest bowling sample of all (369 balls); takes MORE wickets and concedes LESS under pressure.",
    "Shadab Khan": "Best all-round bowling profile: powerplay control, middle-overs wickets, and death-overs value.",
    "Abrar Ahmed": "Cheapest pressure economy (4.74) of the entire shortlist, with strong wicket-taking.",
    "Mohammad Nawaz": "Best economy improvement of any bowler (7.12 -> 5.44) with all-round spin utility.",
}


def squad_fit_table() -> pd.DataFrame:
    bat_top10 = load_batting_top10()
    bowl_top10 = load_bowling_top10()
    rows = []
    for _, r in bat_top10.iterrows():
        rows.append({
            "Player": r["player_name"], "Discipline": "Batter", "Rank": int(r["rank"]),
            "Reliability Score": round(r["batting_reliability_score"], 3),
            "Roles": ", ".join(BAT_ROLES.get(r["player_name"], ["Unclassified"])),
            "Why recommended": REASONS.get(r["player_name"], ""),
        })
    for _, r in bowl_top10.iterrows():
        rows.append({
            "Player": r["player_name"], "Discipline": "Bowler", "Rank": int(r["rank"]),
            "Reliability Score": round(r["bowling_reliability_score"], 3),
            "Roles": ", ".join(BOWL_ROLES.get(r["player_name"], ["Unclassified"])),
            "Why recommended": REASONS.get(r["player_name"], ""),
        })
    return pd.DataFrame(rows)


def players_for_role(role: str) -> pd.DataFrame:
    table = squad_fit_table()
    return table[table["Roles"].str.contains(role, na=False)]


def fit_matrix() -> pd.DataFrame:
    players = list(BAT_ROLES.keys()) + list(BOWL_ROLES.keys())
    all_roles = {**BAT_ROLES, **BOWL_ROLES}
    data = {role: [1 if role in all_roles[p] else 0 for p in players] for role in ALL_ROLES}
    return pd.DataFrame(data, index=players)
