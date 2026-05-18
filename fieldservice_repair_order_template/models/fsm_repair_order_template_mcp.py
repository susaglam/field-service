# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_repair_order_template.

Exposes the fields this module adds to fsm.template as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceRepairOrderTemplateMcp(models.Model):
    _inherit = "fsm.template"

    @ai_tool(
        name="fsm_repair_template.get_repair_template",
        description="Return the linked MRP repair-order template for an FSM template.",
        input_schema={
            "type": "object",
            "properties": {"template_id": {"type": "integer"}},
            "required": ["template_id"],
        },
        risk="low",
    )
    def action_mcp_read(self, template_id):
        rec = self.browse(template_id).exists()
        if not rec:
            return {"error": f"Record {template_id} not found"}
        return {
            "id": rec.id,
            "name": rec.display_name,
            "repair_order_template_id": rec.repair_order_template_id.display_name if rec.repair_order_template_id else None,
            "type_internal": rec.type_internal,
        }
