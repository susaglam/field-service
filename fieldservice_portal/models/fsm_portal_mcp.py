# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_portal.

Exposes the fields this module adds to fsm.stage as one small read tool
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


class FieldservicePortalMcp(models.Model):
    _inherit = "fsm.stage"

    @ai_tool(
        name="fsm_portal.is_stage_visible",
        description="Check if an FSM stage is visible in the customer portal.",
        input_schema={
            "type": "object",
            "properties": {"stage_id": {"type": "integer"}},
            "required": ["stage_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, stage_id):
        rec = self.browse(stage_id).exists()
        if not rec:
            return {"error": f"Record {stage_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "portal_visible": rec.portal_visible,
        }
