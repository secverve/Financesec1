from typing import Optional

from app.fds.base import BaseRule, RuleResult


class NewDeviceHighAmountRule(BaseRule):
    rule_code = "R001"
    rule_name = "신규 디바이스 고액 주문"
    score = 35
    severity = "MEDIUM"
    reason_template = "신규 디바이스에서 최근 평균 주문금액 대비 {multiplier:.1f}배 높은 주문이 접수되었습니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        if context["is_new_device"] and context["order_amount"] >= context["avg_order_amount"] * 3:
            multiplier = context["order_amount"] / max(context["avg_order_amount"], 1)
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template.format(multiplier=multiplier))
        return None


class OverseasImmediateTradeRule(BaseRule):
    rule_code = "R002"
    rule_name = "해외 IP 로그인 후 즉시 주문"
    score = 45
    severity = "HIGH"
    reason_template = "해외 IP 또는 비정상 지역 로그인 직후 주문이 발생했습니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        if context["recent_login_region"].startswith("OVERSEAS"):
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template)
        return None
