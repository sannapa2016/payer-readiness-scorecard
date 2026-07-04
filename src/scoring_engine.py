"""
scoring_engine.py
=================
4-dimension weighted scoring engine for payer readiness.

SCORING DIMENSIONS AND WEIGHTS
--------------------------------
Coverage score      35% -- formulary tier determines patient access
PA burden score     30% -- PA denial and criteria alignment
Step therapy score  20% -- each step = weeks of patient delay
Rebate position     15% -- competitive rebate risk

WHY THESE WEIGHTS
-----------------
Coverage is 35% because formulary access is the gating factor.
No coverage = no prescriptions regardless of everything else.

PA burden is 30% because a Tier 2 payer with 28% PA denials
is worse than a Tier 3 payer with 0% denials. PA is the hidden
access barrier that formulary tier alone does not reveal.

Step therapy is 20% because each step costs the patient weeks
of delay and costs the brand lost revenue during that window.

Rebate position is 15% because it drives future formulary risk
but is less immediately visible than the other three dimensions.

Author: Siva Annapareddy
Domain: Market Access and Pricing Analytics
"""

from dataclasses import dataclass
from typing import Dict
from src.payer_profiles import PayerProfile


@dataclass
class PayerScore:
    """
    Stores all four dimension scores and the composite for one payer.
    """
    payer_id:          str
    coverage_score:    float
    pa_burden_score:   float
    step_therapy_score: float
    rebate_score:      float
    composite_score:   float
    weighted_details:  Dict[str, float]


class ScoringEngine:
    """
    Computes 4-dimension weighted readiness score for each payer.

    WEIGHTS
    -------
    Coverage:      0.35
    PA burden:     0.30
    Step therapy:  0.20
    Rebate:        0.15
    Total:         1.00
    """

    WEIGHTS = {
        "coverage":     0.35,
        "pa_burden":    0.30,
        "step_therapy": 0.20,
        "rebate":       0.15,
    }

    # Formulary tier to raw score mapping
    # Non-formulary is not zero because patient can still
    # get drug via exception — but access is severely limited
    TIER_SCORES = {
        "tier1":          1.00,
        "tier2":          0.85,
        "tier3":          0.60,
        "non_formulary":  0.20,
        "not_submitted":  0.00,
    }

    def score_coverage(self, payer: PayerProfile) -> float:
        """
        Coverage score based on formulary tier.

        WHY NOT LINEAR
        --------------
        The difference between Tier 1 and Tier 2 is smaller than
        the difference between Tier 2 and Tier 3 in practice.
        Higher copay on Tier 3 creates a non-linear drop in access.
        The scores reflect real-world utilization impact not just
        a simple 1-2-3 ranking.
        """
        return self.TIER_SCORES.get(payer.formulary_tier, 0.0)

    def score_pa_burden(self, payer: PayerProfile) -> float:
        """
        PA burden score combining criteria alignment and decision time.

        FORMULA
        -------
        Base score = criteria alignment (0.0 to 1.0)
        If no PA required: score = 1.0 (best case)
        Time penalty: each day beyond 3 days reduces score by 0.03
        Floor at 0.10 so the score never goes to zero from time alone

        WHY PA CRITERIA ALIGNMENT MATTERS
        -----------------------------------
        A payer can have PA but with criteria that match the label
        exactly. That is a low-burden PA. A payer can also have PA
        with criteria that restrict access to a narrower population
        than the FDA approved. That is a high-burden PA that
        effectively shrinks the addressable patient population.
        """
        if not payer.pa_required:
            return 1.00

        base = payer.pa_criteria_alignment

        # Time penalty: days beyond 3 day standard
        time_penalty = max(0, (payer.pa_decision_days - 3) * 0.03)

        return max(0.10, base - time_penalty)

    def score_step_therapy(self, payer: PayerProfile) -> float:
        """
        Step therapy score based on number of required steps.

        STEP COST IN WEEKS
        -------------------
        Each step therapy requirement costs the patient approximately
        4 to 8 weeks of treatment delay while they try and fail the
        required alternative. The score reflects this delay burden.

        0 steps: 1.00 -- no delay
        1 step:  0.75 -- 4-8 weeks delay
        2 steps: 0.50 -- 8-16 weeks delay
        3 steps: 0.25 -- 12-24 weeks delay
        4+ steps: 0.10 -- effectively blocks access
        """
        step_scores = {0: 1.00, 1: 0.75, 2: 0.50, 3: 0.25}
        return step_scores.get(payer.step_therapy_steps, 0.10)

    def score_rebate_position(self, payer: PayerProfile) -> float:
        """
        Rebate position score comparing our rebate to competitor.

        WHY REBATE POSITION MATTERS
        ----------------------------
        If our rebate is significantly higher than the competitor,
        we are paying more to maintain the same formulary position.
        That erodes margin and signals vulnerability to being
        outbid by the competitor at next contract renewal.

        The score rewards competitive or better rebate position
        and penalizes being significantly above competitor rate.
        """
        diff = payer.our_rebate_pct - payer.competitor_rebate_pct

        if diff <= 0:
            return 1.00    # We are at or below competitor — strong position
        elif diff <= 0.05:
            return 0.80    # 1-5% above competitor — slight disadvantage
        elif diff <= 0.10:
            return 0.60    # 5-10% above — meaningful disadvantage
        elif diff <= 0.20:
            return 0.35    # 10-20% above — at risk at renewal
        else:
            return 0.10    # More than 20% above — critical risk

    def score_payer(self, payer: PayerProfile) -> PayerScore:
        """
        Compute all four dimension scores and weighted composite.
        """
        coverage    = self.score_coverage(payer)
        pa_burden   = self.score_pa_burden(payer)
        step        = self.score_step_therapy(payer)
        rebate      = self.score_rebate_position(payer)

        composite = (
            coverage  * self.WEIGHTS["coverage"] +
            pa_burden * self.WEIGHTS["pa_burden"] +
            step      * self.WEIGHTS["step_therapy"] +
            rebate    * self.WEIGHTS["rebate"]
        )

        weighted_details = {
            "coverage_weighted":     round(coverage  * self.WEIGHTS["coverage"]  * 100, 1),
            "pa_burden_weighted":    round(pa_burden * self.WEIGHTS["pa_burden"] * 100, 1),
            "step_therapy_weighted": round(step      * self.WEIGHTS["step_therapy"] * 100, 1),
            "rebate_weighted":       round(rebate    * self.WEIGHTS["rebate"]    * 100, 1),
        }

        return PayerScore(
            payer_id=payer.payer_id,
            coverage_score=round(coverage, 3),
            pa_burden_score=round(pa_burden, 3),
            step_therapy_score=round(step, 3),
            rebate_score=round(rebate, 3),
            composite_score=round(composite * 100, 1),
            weighted_details=weighted_details,
        )

    def score_all(self, payers: dict) -> Dict[str, PayerScore]:
        """Score every payer in the universe."""
        return {pid: self.score_payer(p) for pid, p in payers.items()}


if __name__ == "__main__":
    from src.payer_profiles import build_payer_universe
    payers = build_payer_universe()
    engine = ScoringEngine()
    scores = engine.score_all(payers)

    print(f"{'ID':<6} {'Payer':<30} {'Coverage':<10} {'PA Burden':<12} {'Step':<8} {'Rebate':<10} {'COMPOSITE'}")
    print("-" * 85)
    for pid, s in sorted(scores.items(), key=lambda x: -x[1].composite_score):
        print(f"{pid:<6} {payers[pid].name:<30} "
              f"{s.coverage_score:<10.3f} {s.pa_burden_score:<12.3f} "
              f"{s.step_therapy_score:<8.3f} {s.rebate_score:<10.3f} "
              f"{s.composite_score}")