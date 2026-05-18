# Copyright 2026 saas-19.3 port
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""MCP / @ai_tool surface for account.payment ↔ FSM-order link."""

from odoo import models
from odoo.addons.cs_mcp_bridge.tools import ai_tool


class FsmOrderPaymentMcp(models.Model):
    _inherit = "fsm.order"

    @ai_tool(
        name="fsm_account_payment.list_payments",
        description=(
            "List payments registered against an FSM order. Returns "
            "id, name, state, amount, journal, partner."
        ),
        input_schema={
            "type": "object",
            "properties": {"order_id": {"type": "integer"}},
            "required": ["order_id"],
        },
        risk="low",
    )
    def action_mcp_list_payments(self, order_id):
        order = self.browse(order_id).exists()
        if not order:
            return {"error": f"Order {order_id} not found"}
        return {
            "order_id": order_id,
            "order_name": order.name,
            "payment_count": order.payment_count,
            "payments": [
                {
                    "id": p.id,
                    "name": p.name,
                    "state": p.state,
                    "amount": p.amount,
                    "journal": p.journal_id.name if p.journal_id else None,
                    "partner": p.partner_id.name if p.partner_id else None,
                }
                for p in order.payment_ids
            ],
        }
