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
        self.reports = TreeMap()
        self.profiles = TreeMap()

    @gl.public.write
    def analyze_protocol(self, protocol: str, amount: int, risk_tolerance: str) -> None:
        sender = gl.message.sender_address
        self.profiles[sender] = risk_tolerance

        def _build_analysis() -> str:
            # Web Fetch 1 — дані протоколу з DeFiLlama
            protocol_slug = protocol.lower().replace(" ", "-")
            llama_url = f"https://api.llama.fi/protocol/{protocol_slug}"
            llama_response = gl.nondet.web.get(llama_url)
            protocol_data = llama_response.body.decode("utf-8")[:500]

            # Web Fetch 2 — глобальний TVL для контексту
            global_url = "https://api.llama.fi/v2/globalCharts"
            global_response = gl.nondet.web.get(global_url)
            global_data = global_response.body.decode("utf-8")[:300]

            prompt = f"""You are a DeFi risk and security analyst.

Protocol: {protocol}
Investment amount: ${amount}
Risk tolerance: {risk_tolerance}

Live DeFiLlama data:
{protocol_data}

Global DeFi context:
{global_data}

Return ONLY a valid JSON object:
{{
  "risk_score": <1-10>,
  "risk_level": "<low|medium|high>",
  "tvl_usd": "<e.g. $8.2B>",
  "tvl_trend": "<growing|stable|declining>",
  "audit_status": "<audited|unaudited|unknown>",
  "audit_firms": ["<firm1>", "<firm2>"],
  "incident_risk": "<low|medium|high>",
  "recommendation": "<1-2 sentences>",
  "warnings": ["<warning1>", "<warning2>"],
  "suggested_allocation": <0-100>
}}

No markdown, no extra text, only JSON."""

            return gl.nondet.exec_prompt(prompt)

        result_raw = gl.eq_principle.prompt_comparative(
            _build_analysis,
            "Outputs are equivalent if risk_level, audit_status, and tvl_trend match.",
        )

        # Парсинг результату
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

        if sender not in self.reports:
            self.reports[sender] = DynArray()
        self.reports[sender].append(report)

    @gl.public.view
    def get_reports(self, user: Address) -> str:
        if user not in self.reports:
            return "[]"
        return json.dumps([r.__dict__ for r in self.reports[user]])

    @gl.public.view
    def get_reports_len(self, user: Address) -> int:
        if user not in self.reports:
            return 0
        return len(self.reports[user])

    @gl.public.view
    def get_profile(self, user: Address) -> str:
        if user not in self.profiles:
            return ""
        return self.profiles[user]

    @gl.public.view
    def get_all_reports(self) -> str:
        result = {}
        for addr, reports in self.reports.items():
            result[str(addr)] = len(reports)
        return json.dumps(result)
