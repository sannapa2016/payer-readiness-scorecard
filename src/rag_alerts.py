"""
rag_alerts.py
=============
RAG status assignment and PA denial rate early warning system.

RAG THRESHOLDS
--------------
GREEN  : composite score >= 70  -- good access, monitor quarterly
AMBER  : composite score 45-69  -- monitor monthly, prepare action plan
RED    : composite score < 45   -- immediate escalation required

PA DENIAL RATE THRESHOLDS
--------------------------
WARNING : denial rate > 15%  -- review denial reasons, brief field force
ALERT   : denial rate > 25%  -- escalate to VP Market Access within 5 days

WHY THESE THRESHOLDS
---------------------
Industry benchmark for specialty drug PA approval rate is 80-85%.
Above 85% approval (below 15% denial) = healthy access.
75-85% approval (15-25% denial) = warning zone, investigate.
Below 75% approval (above 25% denial) = systemic problem, escalate.

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

import pandas as pd
from typing import Dict, List
from src.payer_profiles import PayerProfile, build_payer_universe
from src.scoring_engine import ScoringEngine, PayerScore


# RAG thresholds
GREEN_THRESHOLD = 70.0
AMBER_THRESHOLD = 45.0

# PA denial rate thresholds
PA_WARNING_THRESHOLD = 0.15
PA_ALERT_THRESHOLD   = 0.25


def assign_rag(composite_score: float) -> str:
    """
    Assign RAG status based on composite score.

    WHY THREE TIERS NOT TWO
    -----------------------
    A binary pass/fail misses the important middle zone where
    a payer is not yet a crisis but needs active management.
    AMBER gives the brand team a clear signal to prepare
    a remediation plan before the situation turns RED.
    """
    if composite_score >= GREEN_THRESHOLD:
        return "GREEN"
    elif composite_score >= AMBER_THRESHOLD:
        return "AMBER"
    else:
        return "RED"


def check_pa_alerts(payers: Dict[str, PayerProfile]) -> List[dict]:
    """
    Check PA denial rates across all payers and generate alerts.

    Returns list of alert dicts sorted by severity then denial rate.
    Only fires for payers with post-launch denial rate data.
    """
    alerts = []
    for pid, p in payers.items():
        if p.pa_denial_rate is None:
            continue

        if p.pa_denial_rate > PA_ALERT_THRESHOLD:
            severity = "ALERT"
            action = (
                f"Escalate to VP Market Access immediately. "
                f"Schedule payer meeting within 5 days. "
                f"Pull PA denial reason codes. "
                f"Brief field force on documentation requirements."
            )
        elif p.pa_denial_rate > PA_WARNING_THRESHOLD:
            severity = "WARNING"
            action = (
                f"Review PA denial reasons. "
                f"Brief field force on PA criteria. "
                f"Monitor weekly for 4 weeks."
            )
        else:
            continue

        alerts.append({
            "payer_id":       pid,
            "payer_name":     p.name,
            "channel":        p.channel,
            "denial_rate":    f"{p.pa_denial_rate:.0%}",
            "severity":       severity,
            "action_required": action,
        })

    return sorted(alerts, key=lambda x: (
        0 if x["severity"] == "ALERT" else 1,
        -float(x["denial_rate"].strip("%")) / 100
    ))


def build_scorecard(
    payers: Dict[str, PayerProfile],
    scores: Dict[str, PayerScore]
) -> pd.DataFrame:
    """
    Build the master scorecard DataFrame combining profiles and scores.

    Each row is one payer. Columns cover all four scoring dimensions,
    RAG status, PA denial alert, and covered lives weighting.
    """
    rows = []
    for pid, p in payers.items():
        s = scores[pid]
        rag = assign_rag(s.composite_score)

        denial_pct = f"{p.pa_denial_rate:.0%}" if p.pa_denial_rate else "N/A"
        if p.pa_denial_rate and p.pa_denial_rate > PA_ALERT_THRESHOLD:
            pa_alert = "ALERT"
        elif p.pa_denial_rate and p.pa_denial_rate > PA_WARNING_THRESHOLD:
            pa_alert = "WARNING"
        else:
            pa_alert = "OK"

        rows.append({
            "payer_id":          pid,
            "payer_name":        p.name,
            "channel":           p.channel,
            "covered_lives_M":   p.covered_lives_millions,
            "formulary_tier":    p.formulary_tier,
            "coverage_score":    s.coverage_score,
            "pa_burden_score":   s.pa_burden_score,
            "step_score":        s.step_therapy_score,
            "rebate_score":      s.rebate_score,
            "composite_score":   s.composite_score,
            "rag_status":        rag,
            "pa_denial_rate":    denial_pct,
            "pa_alert":          pa_alert,
        })

    df = pd.DataFrame(rows).sort_values("composite_score", ascending=False)
    return df.reset_index(drop=True)


def channel_summary(scorecard: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate scorecard to channel level.

    Shows average composite score, RAG distribution, and
    total covered lives per channel. Used for executive summary.
    """
    rows = []
    for channel in scorecard["channel"].unique():
        ch = scorecard[scorecard["channel"] == channel]
        rows.append({
            "channel":          channel,
            "payer_count":      len(ch),
            "covered_lives_M":  ch["covered_lives_M"].sum(),
            "avg_composite":    round(ch["composite_score"].mean(), 1),
            "green_count":      (ch["rag_status"] == "GREEN").sum(),
            "amber_count":      (ch["rag_status"] == "AMBER").sum(),
            "red_count":        (ch["rag_status"] == "RED").sum(),
            "alert_count":      (ch["pa_alert"] == "ALERT").sum(),
        })

    return pd.DataFrame(rows).sort_values("covered_lives_M", ascending=False)


if __name__ == "__main__":
    payers = build_payer_universe()
    engine = ScoringEngine()
    scores = engine.score_all(payers)

    scorecard = build_scorecard(payers, scores)
    alerts = check_pa_alerts(payers)
    summary = channel_summary(scorecard)

    print("=" * 70)
    print("PAYER READINESS SCORECARD")
    print("=" * 70)
    print()
    print(scorecard[[
        "payer_name", "channel", "composite_score",
        "rag_status", "pa_denial_rate", "pa_alert"
    ]].to_string(index=False))

    print("\nCHANNEL SUMMARY\n")
    print(summary.to_string(index=False))

    print(f"\nPA DENIAL ALERTS ({len(alerts)} fired)\n")
    for a in alerts:
        print(f"[{a['severity']}] {a['payer_name']} — {a['denial_rate']} denial rate")
        print(f"  Action: {a['action_required']}")
        print()