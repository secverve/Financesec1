from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleResult:
    rule_code: str
    rule_name: str
    score: int
    severity: str
    reason: str


class BaseRule:
    rule_code = "BASE"
    rule_name = "Base Rule"
    score = 0
    severity = "LOW"
    reason_template = ""

    def evaluate(self, context: dict) -> Optional[RuleResult]:
        raise NotImplementedError
