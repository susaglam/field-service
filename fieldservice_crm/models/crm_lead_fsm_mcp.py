# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for crm.lead ↔ FSM-order link."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class CrmLeadFsmMcp(models.Model):
    _inherit = "crm.lead"

    @ai_tool(
        name="fsm_crm.list_fsm_orders",
        description=(
            "List Field Service orders linked to a CRM opportunity/lead. "
            "Returns id, name, stage, scheduled date."
        ),
        input_schema={
            "type": "object",
            "properties": {"lead_id": {"type": "integer"}},
            "required": ["lead_id"],
        },
        risk="low",
    )
    def action_mcp_list_fsm(self, lead_id):
        lead = self.browse(lead_id).exists()
        if not lead:
            return {"error": f"Lead {lead_id} not found"}
        return {
            "lead_id": lead.id,
            "lead_name": lead.name,
            "fsm_location": lead.fsm_location_id.display_name
            if lead.fsm_location_id
            else None,
            "fsm_order_count": lead.fsm_order_count,
            "fsm_orders": [
                {"id": o.id, "name": o.name, "stage": o.stage_id.name}
                for o in lead.fsm_order_ids
            ],
        }
