from __future__ import annotations
import httpx
from ..base import SkillBase
from ..types import ParamType, SkillDefinition, SkillParam, SkillResult

LEEPA = "https://leepa.org/Search/PropertySearch.aspx"
TAXDEED = "https://lee.realtaxdeed.com/index.cfm?zaction=AUCTION&zmethod=PREVIEW"
FORECLOSE = "https://www.lee.realforeclose.com/index.cfm?zaction=AUCTION&zmethod=PREVIEW"

class ScoutPrimeSkill(SkillBase):
    """Lee County property intelligence — LEEPA lookups + auction scraping."""

    def definition(self) -> SkillDefinition:
        return SkillDefinition(
            name="scout_prime",
            description="Lee County property intel. Actions: lookup (address or folio) | auctions (upcoming tax deed / foreclosure list)",
            params=[
                SkillParam(name="action", param_type=ParamType.STRING, description="lookup | auctions"),
                SkillParam(name="address", param_type=ParamType.STRING, description="Property address", required=False, default=""),
                SkillParam(name="folio", param_type=ParamType.STRING, description="Folio number", required=False, default=""),
            ],
            category="pantheon",
            timeout_seconds=45.0,
        )

    async def execute(self, action: str, address: str = "", folio: str = "", **kwargs) -> SkillResult:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as c:
            if action == "lookup":
                query = folio or address
                if not query:
                    return SkillResult(skill_name="scout_prime", success=False, output="", error="Provide address or folio.")
                r = await c.get(LEEPA, params={"SearchTerm": query})
                return SkillResult(skill_name="scout_prime", success=r.status_code == 200,
                    output=f"LEEPA [{query}]:\n{r.text[:3000]}" if r.status_code == 200 else "",
                    error="" if r.status_code == 200 else f"HTTP {r.status_code}")

            elif action == "auctions":
                td = await c.get(TAXDEED)
                fc = await c.get(FORECLOSE)
                out = f"--- Tax Deeds (HTTP {td.status_code}) ---\n{td.text[:1500]}\n\n--- Foreclosures (HTTP {fc.status_code}) ---\n{fc.text[:1500]}"
                return SkillResult(skill_name="scout_prime", success=True, output=out)

        return SkillResult(skill_name="scout_prime", success=False, output="", error=f"Unknown action: {action}")
