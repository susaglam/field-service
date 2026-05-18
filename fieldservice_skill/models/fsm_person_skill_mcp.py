# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.person.skill."""

from odoo import models
try:
    from odoo.addons.cs_mcp_bridge.tools import ai_tool
except ImportError:
    # No-op fallback when cs_mcp_bridge is not installed.
    # AI/MCP surface unavailable; methods stay normal callable Python.
    def ai_tool(**_kwargs):
        def _decorator(fn):
            return fn
        return _decorator


class FsmPersonSkillMcp(models.Model):
    _inherit = "fsm.person.skill"

    @ai_tool(
        name="fsm_skill.list_by_person",
        description=(
            "List all skills of a given Field Service worker, with their "
            "level + progress percentage."
        ),
        input_schema={
            "type": "object",
            "properties": {"person_id": {"type": "integer"}},
            "required": ["person_id"],
        },
        risk="low",
    )
    def action_mcp_list(self, person_id):
        rows = self.search([("person_id", "=", person_id)])
        return {
            "person_id": person_id,
            "skills": [
                {
                    "skill_id": r.skill_id.id,
                    "skill": r.skill_id.name,
                    "skill_type": r.skill_type_id.name if r.skill_type_id else None,
                    "level": r.skill_level_id.name if r.skill_level_id else None,
                    "progress": r.level_progress,
                }
                for r in rows
            ],
        }

    @ai_tool(
        name="fsm_skill.find_workers",
        description=(
            "Find Field Service workers who have all the requested skills "
            "at the given minimum level (progress %)."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "skill_ids": {"type": "array", "items": {"type": "integer"}},
                "min_progress": {"type": "number", "default": 0},
            },
            "required": ["skill_ids"],
        },
        risk="low",
    )
    def action_mcp_find_workers(self, skill_ids, min_progress=0):
        rows = self.search(
            [
                ("skill_id", "in", skill_ids),
                ("level_progress", ">=", min_progress),
            ]
        )
        by_person = {}
        for r in rows:
            by_person.setdefault(r.person_id.id, set()).add(r.skill_id.id)
        wanted = set(skill_ids)
        qualified = [
            pid for pid, sids in by_person.items() if wanted.issubset(sids)
        ]
        persons = self.env["fsm.person"].browse(qualified)
        return {
            "count": len(persons),
            "workers": [{"id": p.id, "name": p.name} for p in persons],
        }
