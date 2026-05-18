# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_stock.

Exposes the fields this module adds to fsm.order as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceStockMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_stock.get_stock_info",
        description="Return stock info (warehouse, inv-location, deliveries, returns, transfers) for an FSM order.",
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, order_id):
        rec = self.browse(order_id).exists()
        if not rec:
            return {"error": f"Record {order_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "inventory_location_id": rec.inventory_location_id.display_name if rec.inventory_location_id else None,
            "warehouse_id": rec.warehouse_id.display_name if rec.warehouse_id else None,
            "delivery_count": rec.delivery_count,
            "return_count": rec.return_count,
            "move_ids": [x.id for x in rec.move_ids],
            "picking_ids": [x.id for x in rec.picking_ids],
        }
