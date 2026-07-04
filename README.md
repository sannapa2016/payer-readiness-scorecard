# Payer Landscape Readiness Scorecard

**Pre-Launch Payer Coverage Dashboard with PA Denial Rate Early Warning**

---

## The Problem

A drug launches with Tier 2 formulary coverage at a major PBM.
The brand team celebrates. Eight weeks later claims data shows
volume 40 percent below forecast. The PA denial rate was 28 percent
from week 2. Nobody knew until it was too late.

This scorecard surfaces access problems in week 2 not month 3.

---

## What This Model Does

- Scores 12 payers across 4 dimensions with weighted composite scoring
- Assigns RAG status to every payer — Green, Amber, or Red
- Runs PA denial rate early warning alerts post-launch
- Aggregates to channel-level coverage summary for executive reporting
- Exports full scorecard, channel summary, and alert log to CSV

---

## Model Assumptions

| Parameter | Value | Notes |
|---|---|---|
| Payers scored | 12 | Commercial, Part D, Medicaid, Managed Medicaid |
| Scoring dimensions | 4 | Coverage, PA burden, Step therapy, Rebate position |
| Coverage weight | 35% | Formulary tier is the gating access factor |
| PA burden weight | 30% | PA denial rate is the hidden access barrier |
| Step therapy weight | 20% | Each step = 4-8 weeks patient delay |
| Rebate weight | 15% | Competitive rebate position drives renewal risk |
| PA warning threshold | 15% | Monitor closely, brief field force |
| PA alert threshold | 25% | Escalate to VP Market Access within 5 days |

---

## Key Output

Best payer:   Anthem BCBS — score 97.0  (GREEN)
Worst payer:  New York Medicaid — score 49.7  (AMBER)
Score range:  47.3 points
RAG Summary: 7 GREEN  |  3 AMBER  |  2 RED
PA Alerts fired: 3 ALERT  |  3 WARNING

---

## The Four Scoring Dimensions

| Dimension | Weight | What It Measures |
|---|---|---|
| Coverage | 35% | Formulary tier — Tier 1 to non-formulary |
| PA burden | 30% | PA criteria alignment and decision time |
| Step therapy | 20% | Number of required treatment steps before coverage |
| Rebate position | 15% | Our rebate vs competitor at same payer |

---

## PA Denial Rate Alert System

| Threshold | Status | Action |
|---|---|---|
| Below 15% | OK | Monitor quarterly |
| 15% to 25% | WARNING | Review denial reasons, brief field force weekly |
| Above 25% | ALERT | Escalate to VP Market Access, payer meeting within 5 days |

---

## Quick Start

```bash
git clone https://github.com/sannapa2016/payer-readiness-scorecard.git
cd payer-readiness-scorecard
pip install -r requirements.txt
pip install -e .
python main.py
```

---

## Project Structure

payer-readiness-scorecard/
├── src/
│   ├── init.py           Makes src a Python package
│   ├── payer_profiles.py     12 payer definitions across 4 channels
│   ├── scoring_engine.py     4-dimension weighted scoring engine
│   └── rag_alerts.py         RAG status and PA denial rate alerts
├── outputs/                  CSV results generated on run
├── main.py                   Single entry point
├── requirements.txt          numpy, pandas
└── setup.py                  Makes project installable for any user

---

## Author

**Siva Annapareddy**
Founder and AVP, Amrak Pharma Analytics
18 years in pharma commercial analytics

*Project 3 of 36 — open-source pharma analytics portfolio*

