# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_purchase.

Exposes the fields this module adds to fsm.person as one small read tool
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


class FieldservicePurchaseMcp(models.Model):
    _inherit = "fsm.person"

    @ai_tool(
        name="fsm_purchase.get_pricelist_count",
        description="Return the number of purchase pricelists linked to a worker.",
        input_schema={
            "type": "object",
            "properties": {"person_id": {"type": "integer"}},
            "required": ["person_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, person_id):
        rec = self.browse(person_id).exists()
        if not rec:
            return {"error": f"Record {person_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "pricelist_count": rec.pricelist_count,
        }
