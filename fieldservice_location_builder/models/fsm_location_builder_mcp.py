# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for fsm.location.builder.wizard."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmLocationLevelMcp(models.TransientModel):
    _inherit = "fsm.location.level"

    @ai_tool(
        name="fsm_location_builder.list_levels",
        description=(
            "List configured location hierarchy levels (used by the "
            "location-builder wizard to bulk-create sub-locations)."
        ),
        input_schema={"type": "object", "properties": {}},
        risk="low",
    )
    def action_mcp_list_levels(self):
        rows = self.search([])
        return {
            "count": len(rows),
            "levels": [
                {
                    "id": lv.id,
                    "name": lv.name,
                    "sequence": lv.sequence,
                    "start_number": lv.start_number,
                    "end_number": lv.end_number,
                    "total": lv.total_number,
                    "spacer": lv.spacer,
                }
                for lv in rows
            ],
        }
