# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_equipment_warranty.

Exposes the fields this module adds to fsm.equipment as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceEquipmentWarrantyMcp(models.Model):
    _inherit = "fsm.equipment"

    @ai_tool(
        name="fsm_equipment_warranty.get_warranty",
        description="Return warranty info (duration, start, end, type) for FSM equipment.",
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
            "product_warranty": rec.product_warranty,
            "warranty_start_date": rec.warranty_start_date.isoformat() if rec.warranty_start_date else None,
            "warranty_end_date": rec.warranty_end_date.isoformat() if rec.warranty_end_date else None,
            "product_warranty_type": rec.product_warranty_type,
        }
