# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for change_log."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class ChangeLogMcp(models.Model):
    _inherit = "change_log"

    @ai_tool(
        name="change_log.search",
        description=(
            "Search change logs by title, location, stage, impact, or "
            "type. Returns id, title, location, stage, impact, type, user."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "title_contains": {"type": "string"},
                "location_id": {"type": "integer"},
                "stage_name": {"type": "string"},
                "impact_name": {"type": "string"},
                "type_name": {"type": "string"},
                "limit": {"type": "integer", "default": 30},
            },
        },
        risk="low",
    )
    def action_mcp_search(
        self,
        title_contains=None,
        location_id=None,
        stage_name=None,
        impact_name=None,
        type_name=None,
        limit=30,
    ):
        domain = []
        if title_contains:
            domain.append(("name", "ilike", title_contains))
        if location_id:
            domain.append(("location_id", "=", location_id))
        if stage_name:
            domain.append(("stage_id.name", "ilike", stage_name))
        if impact_name:
            domain.append(("impact_id.name", "ilike", impact_name))
        if type_name:
            domain.append(("type_id.name", "ilike", type_name))
        records = self.search(domain, limit=limit)
        return {
            "count": len(records),
            "logs": [
                {
                    "id": cl.id,
                    "title": cl.name,
                    "location": cl.location_id.display_name
                    if cl.location_id
                    else None,
                    "stage": cl.stage_id.name if cl.stage_id else None,
                    "impact": cl.impact_id.name if cl.impact_id else None,
                    "type": cl.type_id.name if cl.type_id else None,
                    "user": cl.user_id.name if cl.user_id else None,
                    "implemented_on": cl.implemented_on.isoformat()
                    if cl.implemented_on
                    else None,
                }
                for cl in records
            ],
        }

    @ai_tool(
        name="change_log.create",
        description=(
            "Create a new change log entry attached to a Field Service "
            "location."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "location_id": {"type": "integer"},
                "description": {"type": "string"},
                "type_id": {"type": "integer"},
                "impact_id": {"type": "integer"},
            },
            "required": ["title", "location_id"],
        },
        risk="medium",
    )
    def action_mcp_create(
        self, title, location_id, description=None, type_id=None, impact_id=None
    ):
        vals = {"name": title, "location_id": location_id}
        if description:
            vals["description"] = description
        if type_id:
            vals["type_id"] = type_id
        if impact_id:
            vals["impact_id"] = impact_id
        cl = self.create(vals)
        return {"id": cl.id, "title": cl.name, "stage": cl.stage_id.name}
