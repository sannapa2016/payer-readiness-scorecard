"""
payer_profiles.py
=================
Payer profile definitions for the readiness scorecard.

12 payers across 4 channels:
    Commercial:       Express Scripts, CVS Caremark, OptumRx, Anthem BCBS
    Medicare Part D:  UnitedHealth AARP, Humana, SilverScript, WellCare
    Medicaid:         California Medi-Cal, New York Medicaid
    Managed Medicaid: Centene, Molina

WHY A DATACLASS
---------------
Each payer has 12 attributes. A dataclass enforces structure,
gives IDE autocomplete, and makes the code self-documenting.
Same pattern as Market in Project 1 and GTNConfig in Project 2.

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PayerProfile:
    """
    Represents a single payer with all attributes needed for scoring.

    Attributes
    ----------
    payer_id : str
        Short unique identifier used as dict key
    name : str
        Full payer name for display
    channel : str
        commercial | part_d | medicaid | managed_medicaid
    covered_lives_millions : float
        Number of covered lives in millions
        Weights the importance of this payer in portfolio summary
    formulary_tier : str
        tier1 | tier2 | tier3 | non_formulary | not_submitted
    pa_required : bool
        Whether prior authorization is required
    pa_criteria_alignment : float
        How closely PA criteria match the drug label (0.0 to 1.0)
        1.0 = PA criteria match label exactly
        0.5 = PA criteria restrict access beyond label
        0.0 = PA criteria effectively block all access
    pa_decision_days : int
        Average days to PA decision
        Longer = more patient delay = lower score
    step_therapy_steps : int
        Number of step therapy requirements
        0 = no step therapy
        1 = must try one alternative first
        2 = must try two alternatives
    our_rebate_pct : float
        Our contracted rebate as % of WAC
    competitor_rebate_pct : float
        Competitor rebate at same payer as % of WAC
    pa_denial_rate : Optional[float]
        Post-launch PA denial rate (0.0 to 1.0)
        None = pre-launch, not yet available
        0.28 = 28% of PA requests denied
    """
    payer_id:                str
    name:                    str
    channel:                 str
    covered_lives_millions:  float
    formulary_tier:          str
    pa_required:             bool
    pa_criteria_alignment:   float
    pa_decision_days:        int
    step_therapy_steps:      int
    our_rebate_pct:          float
    competitor_rebate_pct:   float
    pa_denial_rate:          Optional[float] = None


def build_payer_universe() -> dict:
    """
    Build the full payer universe for scorecard analysis.

    PAYER MIX RATIONALE
    --------------------
    Commercial PBMs (Express Scripts, CVS, Optum, Anthem) cover
    the majority of commercially insured lives. These payers drive
    net revenue per unit and are the primary contracting targets.

    Part D plans cover Medicare beneficiaries — critical for drugs
    with elderly patient populations (oncology, cardiovascular).

    Medicaid covers low-income populations with high mandatory rebates
    but important volume in high-prevalence disease areas.

    Managed Medicaid (Centene, Molina) is the fastest growing segment
    as states shift Medicaid to managed care organizations.
    """
    return {
        # ── Commercial PBMs ───────────────────────────────────────
        "ESI": PayerProfile(
            payer_id="ESI",
            name="Express Scripts (ESI)",
            channel="commercial",
            covered_lives_millions=95.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.85,
            pa_decision_days=3,
            step_therapy_steps=1,
            our_rebate_pct=0.14,
            competitor_rebate_pct=0.12,
            pa_denial_rate=0.12,
        ),
        "CVS": PayerProfile(
            payer_id="CVS",
            name="CVS Caremark",
            channel="commercial",
            covered_lives_millions=92.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.90,
            pa_decision_days=2,
            step_therapy_steps=0,
            our_rebate_pct=0.13,
            competitor_rebate_pct=0.14,
            pa_denial_rate=0.08,
        ),
        "OPT": PayerProfile(
            payer_id="OPT",
            name="OptumRx",
            channel="commercial",
            covered_lives_millions=67.0,
            formulary_tier="tier3",
            pa_required=True,
            pa_criteria_alignment=0.60,
            pa_decision_days=5,
            step_therapy_steps=2,
            our_rebate_pct=0.11,
            competitor_rebate_pct=0.15,
            pa_denial_rate=0.28,
        ),
        "ANT": PayerProfile(
            payer_id="ANT",
            name="Anthem BCBS",
            channel="commercial",
            covered_lives_millions=45.0,
            formulary_tier="tier1",
            pa_required=False,
            pa_criteria_alignment=1.00,
            pa_decision_days=0,
            step_therapy_steps=0,
            our_rebate_pct=0.16,
            competitor_rebate_pct=0.14,
            pa_denial_rate=0.02,
        ),

        # ── Medicare Part D ───────────────────────────────────────
        "UHC": PayerProfile(
            payer_id="UHC",
            name="UnitedHealth AARP",
            channel="part_d",
            covered_lives_millions=28.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.80,
            pa_decision_days=4,
            step_therapy_steps=1,
            our_rebate_pct=0.18,
            competitor_rebate_pct=0.16,
            pa_denial_rate=0.15,
        ),
        "HUM": PayerProfile(
            payer_id="HUM",
            name="Humana",
            channel="part_d",
            covered_lives_millions=18.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.75,
            pa_decision_days=3,
            step_therapy_steps=1,
            our_rebate_pct=0.17,
            competitor_rebate_pct=0.17,
            pa_denial_rate=0.11,
        ),
        "SIL": PayerProfile(
            payer_id="SIL",
            name="SilverScript (CVS Health)",
            channel="part_d",
            covered_lives_millions=9.0,
            formulary_tier="tier3",
            pa_required=True,
            pa_criteria_alignment=0.55,
            pa_decision_days=6,
            step_therapy_steps=2,
            our_rebate_pct=0.15,
            competitor_rebate_pct=0.18,
            pa_denial_rate=0.32,
        ),
        "WEL": PayerProfile(
            payer_id="WEL",
            name="WellCare",
            channel="part_d",
            covered_lives_millions=7.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.70,
            pa_decision_days=4,
            step_therapy_steps=1,
            our_rebate_pct=0.16,
            competitor_rebate_pct=0.15,
            pa_denial_rate=0.18,
        ),

        # ── Medicaid ──────────────────────────────────────────────
        "CAM": PayerProfile(
            payer_id="CAM",
            name="California Medi-Cal",
            channel="medicaid",
            covered_lives_millions=14.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.65,
            pa_decision_days=7,
            step_therapy_steps=2,
            our_rebate_pct=0.28,
            competitor_rebate_pct=0.28,
            pa_denial_rate=0.20,
        ),
        "NYM": PayerProfile(
            payer_id="NYM",
            name="New York Medicaid",
            channel="medicaid",
            covered_lives_millions=8.0,
            formulary_tier="tier3",
            pa_required=True,
            pa_criteria_alignment=0.50,
            pa_decision_days=10,
            step_therapy_steps=3,
            our_rebate_pct=0.28,
            competitor_rebate_pct=0.28,
            pa_denial_rate=0.35,
        ),

        # ── Managed Medicaid ──────────────────────────────────────
        "CEN": PayerProfile(
            payer_id="CEN",
            name="Centene",
            channel="managed_medicaid",
            covered_lives_millions=16.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.72,
            pa_decision_days=5,
            step_therapy_steps=1,
            our_rebate_pct=0.25,
            competitor_rebate_pct=0.23,
            pa_denial_rate=0.16,
        ),
        "MOL": PayerProfile(
            payer_id="MOL",
            name="Molina Healthcare",
            channel="managed_medicaid",
            covered_lives_millions=9.0,
            formulary_tier="tier2",
            pa_required=True,
            pa_criteria_alignment=0.78,
            pa_decision_days=4,
            step_therapy_steps=1,
            our_rebate_pct=0.24,
            competitor_rebate_pct=0.22,
            pa_denial_rate=0.13,
        ),
    }


if __name__ == "__main__":
    payers = build_payer_universe()
    print(f"Total payers loaded: {len(payers)}")
    print()
    print(f"{'ID':<6} {'Name':<30} {'Channel':<20} {'Lives (M)':<12} {'Tier':<15} {'PA Denial'}")
    print("-" * 95)
    for pid, p in payers.items():
        denial = f"{p.pa_denial_rate:.0%}" if p.pa_denial_rate is not None else "N/A"
        print(f"{pid:<6} {p.name:<30} {p.channel:<20} {p.covered_lives_millions:<12} {p.formulary_tier:<15} {denial}")