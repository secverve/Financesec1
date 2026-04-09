from typing import Optional

from app.fds.base import BaseRule, RuleResult


class RepeatedFailureThenOrderRule(BaseRule):
    rule_code = "R003"
    rule_name = "로그인 실패 반복 후 주문"
    score = 30
    severity = "MEDIUM"
    reason_template = "최근 로그인 실패 이력 {failures}건 이후 주문이 접수되었습니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        failures = context["login_failures"]
        if failures >= 3:
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template.format(failures=failures))
        return None


class AbnormalAmountSpikeRule(BaseRule):
    rule_code = "R004"
    rule_name = "평균 대비 주문금액 급증"
    score = 40
    severity = "HIGH"
    reason_template = "평균 주문금액 대비 {multiplier:.1f}배 높은 주문입니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        if context["order_amount"] >= context["avg_order_amount"] * 5:
            multiplier = context["order_amount"] / max(context["avg_order_amount"], 1)
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template.format(multiplier=multiplier))
        return None


class ConcentratedStockRule(BaseRule):
    rule_code = "R005"
    rule_name = "특정 종목 집중 주문"
    score = 25
    severity = "MEDIUM"
    reason_template = "선호 종목 외 특정 종목에 집중 주문 패턴이 감지되었습니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        preferred = context["preferred_stocks"]
        if context["stock_code"] not in preferred and context["same_stock_order_count"] >= 3:
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template)
        return None


class SameIPMultipleAccountsRule(BaseRule):
    rule_code = "R006"
    rule_name = "동일 IP 다계정 유사 주문"
    score = 50
    severity = "HIGH"
    reason_template = "동일 IP에서 여러 계정의 유사 주문이 발생했습니다."

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        if context["same_ip_order_users"] >= 2:
            return RuleResult(self.rule_code, self.rule_name, self.score, self.severity, self.reason_template)
        return None
