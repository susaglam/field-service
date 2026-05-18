# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_distribution.

Exposes the fields this module adds to fsm.location as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

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


class FieldserviceDistributionMcp(models.Model):
    _inherit = "fsm.location"

    @ai_tool(
        name="fsm_distribution.get_distribution",
        description="Return distribution metadata for an FSM location.",
        input_schema={
            "type": "object",
            "properties": {"location_id": {"type": "integer"}},
            "required": ["location_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, location_id):
        rec = self.browse(location_id).exists()
        if not rec:
            return {"error": f"Record {location_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "is_a_distribution": rec.is_a_distribution,
            "dist_parent_id": rec.dist_parent_id.display_name if rec.dist_parent_id else None,
            "distrib_count": rec.distrib_count,
        }
