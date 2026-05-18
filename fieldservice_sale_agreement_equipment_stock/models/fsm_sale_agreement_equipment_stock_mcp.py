# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_sale_agreement_equipment_stock.

Exposes the fields this module adds to stock.move as one small read tool
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


class FieldserviceSaleAgreementEquipmentStockMcp(models.Model):
    _inherit = "stock.move"

    @ai_tool(
        name="fsm_sale_agreement_stock.get_agreement",
        description="Return the agreement linked to a stock move.",
        input_schema={
            "type": "object",
            "properties": {"move_id": {"type": "integer"}},
            "required": ["move_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, move_id):
        rec = self.browse(move_id).exists()
        if not rec:
            return {"error": f"Record {move_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "agreement_id": rec.agreement_id.display_name if rec.agreement_id else None,
        }
