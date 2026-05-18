# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_sale_stock.

Exposes the fields this module adds to sale.order as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceSaleStockMcp(models.Model):
    _inherit = "sale.order"

    @ai_tool(
        name="fsm_sale_stock.get_fsm_count",
        description="Return FSM order count for a sale order (stock-flow variant).",
        input_schema={
            "type": "object",
            "properties": {"sale_order_id": {"type": "integer"}},
            "required": ["sale_order_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, sale_order_id):
        rec = self.browse(sale_order_id).exists()
        if not rec:
            return {"error": f"Record {sale_order_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "fsm_order_count": rec.fsm_order_count,
        }
