from dataclasses import asdict

from app.fds.rules.behavior_rules import AbnormalAmountSpikeRule, ConcentratedStockRule, RepeatedFailureThenOrderRule, SameIPMultipleAccountsRule
from app.fds.rules.device_rules import NewDeviceHighAmountRule, OverseasImmediateTradeRule


class RiskEngine:
    def __init__(self):
        self.rules = [
            NewDeviceHighAmountRule(),
            OverseasImmediateTradeRule(),
            RepeatedFailureThenOrderRule(),
            AbnormalAmountSpikeRule(),
            ConcentratedStockRule(),
            SameIPMultipleAccountsRule(),
        ]

    def evaluate(self, context: dict) -> dict:
        hits = []
        total_score = 0
        for rule in self.rules:
            result = rule.evaluate(context)
            if result:
                hits.append(asdict(result))
                total_score += result.score

        if total_score >= 80:
            risk_level = "CRITICAL"
            decision = "BLOCK"
        elif total_score >= 60:
            risk_level = "SUSPICIOUS"
            decision = "HOLD"
        elif total_score >= 30:
            risk_level = "CAUTION"
            decision = "ALLOW"
        else:
            risk_level = "NORMAL"
            decision = "ALLOW"

        return {
            "score": total_score,
            "risk_level": risk_level,
            "decision": decision,
            "hits": hits,
        }
