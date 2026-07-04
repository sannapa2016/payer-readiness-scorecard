"""
main.py
=======
Single entry point for the Payer Landscape Readiness Scorecard.

Runs three analyses:
    1. Full payer scorecard with RAG status
    2. Channel summary — aggregated by payer type
    3. PA denial rate early warning alerts

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

import os
import pandas as pd
from src.payer_profiles import build_payer_universe
from src.scoring_engine import ScoringEngine
from src.rag_alerts import build_scorecard, channel_summary, check_pa_alerts

os.makedirs("outputs", exist_ok=True)


def main():
    print("=" * 70)
    print("PAYER LANDSCAPE READINESS SCORECARD")
    print("Author: Siva Annapareddy | Amrak Pharma Analytics")
    print("=" * 70)

    # ── Load data and score ───────────────────────────────────────
    payers = build_payer_universe()
    engine = ScoringEngine()
    scores = engine.score_all(payers)
    scorecard = build_scorecard(payers, scores)
    alerts = check_pa_alerts(payers)
    summary = channel_summary(scorecard)

    # ── Analysis 1: Full scorecard ────────────────────────────────
    print("\n[1] FULL PAYER SCORECARD\n")
    print(scorecard[[
        "payer_name", "channel", "covered_lives_M",
        "formulary_tier", "composite_score",
        "rag_status", "pa_denial_rate", "pa_alert"
    ]].to_string(index=False))

    # RAG summary
    green = (scorecard["rag_status"] == "GREEN").sum()
    amber = (scorecard["rag_status"] == "AMBER").sum()
    red   = (scorecard["rag_status"] == "RED").sum()
    print(f"\n  RAG Summary: {green} GREEN  |  {amber} AMBER  |  {red} RED")

    total_lives = scorecard["covered_lives_M"].sum()
    green_lives = scorecard[scorecard["rag_status"] == "GREEN"]["covered_lives_M"].sum()
    print(f"  GREEN payer coverage: {green_lives:.0f}M of {total_lives:.0f}M total lives ({green_lives/total_lives*100:.0f}%)")

    # ── Analysis 2: Channel summary ───────────────────────────────
    print("\n[2] CHANNEL SUMMARY\n")
    print(summary.to_string(index=False))

    # ── Analysis 3: PA denial alerts ─────────────────────────────
    print(f"\n[3] PA DENIAL RATE ALERTS — {len(alerts)} fired\n")
    alert_count = sum(1 for a in alerts if a["severity"] == "ALERT")
    warn_count  = sum(1 for a in alerts if a["severity"] == "WARNING")
    print(f"  ALERTS (escalate now):     {alert_count}")
    print(f"  WARNINGS (monitor weekly): {warn_count}")
    print()
    for a in alerts:
        print(f"  [{a['severity']}] {a['payer_name']} ({a['channel']}) — {a['denial_rate']} denial rate")
        print(f"  Action: {a['action_required']}")
        print()

    # ── Key insights ──────────────────────────────────────────────
    print("[4] KEY INSIGHTS\n")
    top_payer = scorecard.iloc[0]
    bottom_payer = scorecard.iloc[-1]
    print(f"  Best payer:   {top_payer['payer_name']} — score {top_payer['composite_score']}")
    print(f"  Worst payer:  {bottom_payer['payer_name']} — score {bottom_payer['composite_score']}")
    print(f"  Score range:  {top_payer['composite_score'] - bottom_payer['composite_score']:.1f} points")
    print(f"  Payers needing immediate action: {alert_count + red}")

    # ── Export ────────────────────────────────────────────────────
    scorecard.to_csv("outputs/payer_scorecard.csv", index=False)
    summary.to_csv("outputs/channel_summary.csv", index=False)
    pd.DataFrame(alerts).to_csv("outputs/pa_alerts.csv", index=False)

    print("\n[OK] Results saved to outputs/")
    print("=" * 70)


if __name__ == "__main__":
    main()