# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_equipment_stock.

Exposes the fields this module adds to fsm.equipment as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceEquipmentStockMcp(models.Model):
    _inherit = "fsm.equipment"

    @ai_tool(
        name="fsm_equipment_stock.get_stock_info",
        description="Return current stock-location, product, and lot of an FSM equipment.",
        input_schema={
            "type": "object",
            "properties": {"equipment_id": {"type": "integer"}},
            "required": ["equipment_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, equipment_id):
        rec = self.browse(equipment_id).exists()
        if not rec:
            return {"error": f"Record {equipment_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "current_stock_location_id": rec.current_stock_location_id.display_name if rec.current_stock_location_id else None,
            "product_id": rec.product_id.display_name if rec.product_id else None,
            "lot_id": rec.lot_id.display_name if rec.lot_id else None,
        }
