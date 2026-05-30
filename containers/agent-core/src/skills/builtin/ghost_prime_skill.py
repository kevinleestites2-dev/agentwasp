from __future__ import annotations
import os, httpx
from ..base import SkillBase
from ..types import ParamType, SkillDefinition, SkillParam, SkillResult

REPO = "kevinleestites2-dev/CloakPrime"
WORKFLOW = "ghost.yml"

class GhostPrimeSkill(SkillBase):
    """Control GhostPrime traffic swarm via GitHub Actions."""

    def definition(self) -> SkillDefinition:
        return SkillDefinition(
            name="ghost_prime",
            description="Control the GhostPrime traffic swarm. Actions: status | dispatch | stop",
            params=[SkillParam(name="action", param_type=ParamType.STRING, description="status | dispatch | stop")],
            category="pantheon",
            timeout_seconds=30.0,
        )

    async def execute(self, action: str, **kwargs) -> SkillResult:
        t = os.environ.get("GITHUB_TOKEN", "")
        headers = {"Authorization": f"token {t}", "Accept": "application/vnd.github+json"}

        async with httpx.AsyncClient(timeout=20) as c:
            if action == "status":
                r = await c.get(f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=3", headers=headers)
                runs = r.json().get("workflow_runs", [])
                if not runs:
                    return SkillResult(skill_name="ghost_prime", success=True, output="No runs found.")
                out = "\n".join(f"Run #{x['run_number']}: {x['status']} / {x['conclusion']} — {x['created_at']}" for x in runs)
                return SkillResult(skill_name="ghost_prime", success=True, output=out)

            elif action == "dispatch":
                r = await c.post(f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/dispatches", headers=headers, json={"ref": "main"})
                if r.status_code in (204, 201, 200):
                    return SkillResult(skill_name="ghost_prime", success=True, output="GhostPrime cycle dispatched. Eternal loop engaged.")
                return SkillResult(skill_name="ghost_prime", success=False, output="", error=f"Dispatch failed: HTTP {r.status_code}")

            elif action == "stop":
                r = await c.get(f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?status=in_progress&per_page=5", headers=headers)
                runs = r.json().get("workflow_runs", [])
                if not runs:
                    return SkillResult(skill_name="ghost_prime", success=True, output="No active runs to cancel.")
                results = []
                for run in runs:
                    cr = await c.post(f"https://api.github.com/repos/{REPO}/actions/runs/{run['id']}/cancel", headers=headers)
                    results.append(f"Run #{run['run_number']}: {'cancelled' if cr.status_code == 202 else 'error'}")
                return SkillResult(skill_name="ghost_prime", success=True, output="\n".join(results))

        return SkillResult(skill_name="ghost_prime", success=False, output="", error=f"Unknown action: {action}")
