# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Minimal MCP / @ai_tool surface for fieldservice_agreement.

Exposes the fields this module adds to fsm.order as one small read tool
so AI clients can fetch them without scraping the order_read payload.
"""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FieldserviceAgreementMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_agreement.get_agreement",
        description="Return the agreement (if any) linked to an FSM order.",
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
            "agreement_id": rec.agreement_id.display_name if rec.agreement_id else None,
        }
