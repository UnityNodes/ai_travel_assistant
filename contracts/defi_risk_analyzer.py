# { "Depends": "py-genlayer:test" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class RiskReport:
    protocol: str
    amount: int
    risk_tolerance: str
    risk_score: int
    risk_level: str
    tvl_usd: str
    tvl_trend: str
    audit_status: str
    audit_firms: str
    incident_risk: str
    recommendation: str
    warnings: str
    suggested_allocation: int


class DeFiRiskAnalyzer(gl.Contract):
    reports: TreeMap[Address, DynArray[RiskReport]]
    profiles: TreeMap[Address, str]

    def __init__(self) -> None:
        pass

    @gl.public.write
    def analyze_protocol(self, protocol: str, amount: int, risk_tolerance: str) -> None:
        sender = gl.message.sender_address
        self.profiles[sender] = risk_tolerance

        def _build_analysis() -> str:
            protocol_slug = protocol.lower().replace(" ", "-")
            llama_response = gl.nondet.web.get(f"https://api.llama.fi/protocol/{protocol_slug}")
            protocol_data = llama_response.body.decode("utf-8")[:200]

            prompt = f"""DeFi risk analyst. Return ONLY JSON, no extra text.

Protocol: {protocol}, Amount: ${amount}, Risk tolerance: {risk_tolerance}
DeFiLlama data: {protocol_data}

{{"risk_score":0,"risk_level":"low","tvl_usd":"$1B","tvl_trend":"stable","audit_status":"audited","audit_firms":["OpenZeppelin"],"incident_risk":"low","recommendation":"text","warnings":[],"suggested_allocation":10}}

Fill real values for {protocol}. Return only JSON."""

            return gl.nondet.exec_prompt(prompt)

        result_raw = gl.eq_principle.prompt_comparative(
            _build_analysis,
            "Outputs are equivalent if risk_level, audit_status, and tvl_trend match.",
        )

        clean = result_raw.strip()
        start = clean.find("{")
        end = clean.rfind("}")
        if start >= 0 and end > start:
            clean = clean[start:end + 1]
        result = json.loads(clean)

        report = RiskReport(
            protocol=protocol,
            amount=amount,
            risk_tolerance=risk_tolerance,
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            tvl_usd=result["tvl_usd"],
            tvl_trend=result["tvl_trend"],
            audit_status=result["audit_status"],
            audit_firms=json.dumps(result["audit_firms"]),
            incident_risk=result["incident_risk"],
            recommendation=result["recommendation"],
            warnings=json.dumps(result["warnings"]),
            suggested_allocation=result["suggested_allocation"],
        )

        user_reports = self.reports.get_or_insert_default(sender)
        user_reports.append(report)
        self.reports[sender] = user_reports

    @gl.public.view
    def get_reports(self, user: str) -> str:
        addr = Address(user)
        if addr not in self.reports:
            return "[]"
        return json.dumps([r.__dict__ for r in self.reports[addr]])

    @gl.public.view
    def get_reports_len(self, user: str) -> int:
        addr = Address(user)
        if addr not in self.reports:
            return 0
        return len(self.reports[addr])

    @gl.public.view
    def get_profile(self, user: str) -> str:
        addr = Address(user)
        if addr not in self.profiles:
            return ""
        return self.profiles[addr]

    @gl.public.view
    def get_all_reports(self) -> str:
        result = {}
        for addr, reports in self.reports.items():
            result[str(addr)] = len(reports)
        return json.dumps(result)
