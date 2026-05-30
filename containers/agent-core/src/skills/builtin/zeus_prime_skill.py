from __future__ import annotations
import httpx
from ..base import SkillBase
from ..types import ParamType, SkillDefinition, SkillParam, SkillResult

POLY_BASE = "https://clob.polymarket.com"
WALLET = "0x369c2DDDBEb910c48356910069B2903b3Cb4d535"
API_KEY = "c7b727d4-1cf5-8f32-47f8-a796439e0ca5"

class ZeusPrimeSkill(SkillBase):
    """ZeusPrime on-chain + Polymarket prediction market interface."""

    def definition(self) -> SkillDefinition:
        return SkillDefinition(
            name="zeus_prime",
            description="ZeusPrime on-chain ops. Actions: balance | positions | markets",
            params=[
                SkillParam(name="action", param_type=ParamType.STRING, description="balance | positions | markets"),
                SkillParam(name="market_query", param_type=ParamType.STRING, description="Keyword filter for markets", required=False, default=""),
            ],
            category="pantheon",
            timeout_seconds=30.0,
        )

    async def execute(self, action: str, market_query: str = "", **kwargs) -> SkillResult:
        headers = {"POLY_API_KEY": API_KEY}
        async with httpx.AsyncClient(timeout=20) as c:
            if action == "balance":
                r = await c.get(f"{POLY_BASE}/balance?wallet={WALLET}", headers=headers)
                return SkillResult(skill_name="zeus_prime", success=r.status_code==200,
                    output=f"ZeusPrime wallet {WALLET}:\n{r.text[:2000]}" if r.status_code==200 else "",
                    error="" if r.status_code==200 else f"HTTP {r.status_code}: {r.text[:200]}")

            elif action == "positions":
                r = await c.get(f"{POLY_BASE}/positions?maker={WALLET}", headers=headers)
                return SkillResult(skill_name="zeus_prime", success=r.status_code==200,
                    output=f"Positions:\n{r.text[:3000]}" if r.status_code==200 else "",
                    error="" if r.status_code==200 else f"HTTP {r.status_code}: {r.text[:200]}")

            elif action == "markets":
                params = {"limit": 20, "active": "true"}
                if market_query:
                    params["keyword"] = market_query
                r = await c.get(f"{POLY_BASE}/markets", headers=headers, params=params)
                return SkillResult(skill_name="zeus_prime", success=r.status_code==200,
                    output=f"Markets:\n{r.text[:4000]}" if r.status_code==200 else "",
                    error="" if r.status_code==200 else f"HTTP {r.status_code}: {r.text[:200]}")

        return SkillResult(skill_name="zeus_prime", success=False, output="", error=f"Unknown action: {action}")
