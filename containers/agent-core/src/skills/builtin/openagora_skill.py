from __future__ import annotations
import asyncio, httpx
from ..base import SkillBase
from ..types import ParamType, SkillDefinition, SkillParam, SkillResult

RELAY = "https://nexus-relay-production.up.railway.app"
SECRET = "pantheon_prime"

class OpenAgoraSkill(SkillBase):
    """OpenAgora autonomous arb engine — query via Nexus Relay."""

    def definition(self) -> SkillDefinition:
        return SkillDefinition(
            name="openagora",
            description="Query OpenAgora arb engine on Termux via Nexus Relay. Actions: status | command",
            params=[
                SkillParam(name="action", param_type=ParamType.STRING, description="status | command"),
                SkillParam(name="cmd", param_type=ParamType.STRING, description="Raw command for engine", required=False, default="status"),
            ],
            category="pantheon",
            timeout_seconds=35.0,
        )

    async def execute(self, action: str, cmd: str = "status", **kwargs) -> SkillResult:
        headers = {"X-Secret": SECRET, "Content-Type": "application/json"}
        payload = {"type": "openagora", "cmd": cmd if action == "command" else "status"}
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(f"{RELAY}/command", headers=headers, json=payload)
        if r.status_code not in (200, 201):
            return SkillResult(skill_name="openagora", success=False, output="", error=f"Relay POST {r.status_code}")
        cmd_id = r.json().get("_id")
        await asyncio.sleep(6)
        async with httpx.AsyncClient(timeout=15) as c:
            res = await c.get(f"{RELAY}/result/{cmd_id}", headers=headers)
        if res.status_code == 200:
            return SkillResult(skill_name="openagora", success=True, output=f"OpenAgora [{payload['cmd']}]:\n{res.text[:3000]}")
        return SkillResult(skill_name="openagora", success=True,
            output=f"Command queued (id={cmd_id}). Phone may be offline — check @Seekerclaw27_bot.")
